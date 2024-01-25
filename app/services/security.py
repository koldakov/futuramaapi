from copy import deepcopy
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, Request, status
from fastapi.param_functions import Body
from fastapi.security import OAuth2PasswordBearer
from jose import exceptions, jwt
from pydantic import BaseModel
from typing_extensions import Annotated, Doc

from app.configs import settings

DEFAULT_JWT_EXPIRATION_TIME: int = 15 * 60


class TokenData(BaseModel):
    uuid: str


def generate_jwt_signature(
    payload: dict,
    /,
    *,
    expiration_time: int = DEFAULT_JWT_EXPIRATION_TIME,
    algorithm: str = "HS256",
) -> str:
    cleaned_payload: dict = deepcopy(payload)

    cleaned_payload.update(
        {
            "exp": datetime.now() + timedelta(seconds=expiration_time),
        }
    )

    return jwt.encode(cleaned_payload, settings.secret_key, algorithm=algorithm)


class SignatureErrorBase(Exception):
    """Base JWT Error"""


class FatalSignatureError(SignatureErrorBase):
    """Fatal Signature Error"""


class SignatureExpiredError(SignatureErrorBase):
    """Signature Expired Error"""


def decode_jwt_signature(
    token: str,
    /,
    *,
    algorithms: List[str] = None,
) -> dict:
    if algorithms is None:
        algorithms = ["HS256"]

    try:
        return jwt.decode(token, settings.secret_key, algorithms=algorithms)
    except (exceptions.JWSError, exceptions.JWSSignatureError, exceptions.JWTError):
        raise FatalSignatureError()
    except exceptions.ExpiredSignatureError:
        raise SignatureExpiredError()


class UnauthorizedResponse(BaseModel):
    detail: str


class OAuth2PasswordRequestJson:
    def __init__(
        self,
        *,
        username: Annotated[
            str,
            Body(),
            Doc(
                """
                `username` string. The OAuth2 spec requires the exact field name
                `username`.
                """
            ),
        ],
        password: Annotated[
            str,
            Body(),
            Doc(
                """
                `password` string. The OAuth2 spec requires the exact field name
                `password".
                """
            ),
        ],
    ):
        self.username = username
        self.password = password


class OAuth2JWTBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str | TokenData]:
        param = await super().__call__(request)
        try:
            decoded_token: dict = decode_jwt_signature(param)
        except SignatureExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except FatalSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        return TokenData(**decoded_token)
