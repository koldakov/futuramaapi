from copy import deepcopy
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, Request, status
from fastapi.param_functions import Body
from fastapi.security import OAuth2PasswordBearer
from jose import exceptions, jwt
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Annotated, Doc

from app.core import settings

DEFAULT_JWT_EXPIRATION_TIME: int = 15 * 60
REFRESH_JWT_EXPIRATION_TIME: int = 60 * 60 * 24 * 21


class TokenType(Enum):
    REFRESH = "REFRESH"
    ACCESS = "ACCESS"


class TokenBase(BaseModel):
    type: TokenType


class AccessTokenData(TokenBase):
    uuid: UUID
    type: TokenType = TokenType.ACCESS


class RefreshTokenData(TokenBase):
    nonce: str = Field(min_length=32, max_length=32)
    uuid: UUID
    type: TokenType = TokenType.REFRESH


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
            "exp": datetime.now(UTC) + timedelta(seconds=expiration_time),
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


class OAuth2JWTBearerBase[T](OAuth2PasswordBearer):
    _model: T = None

    def extra_checks(self, model):
        raise NotImplementedError()

    async def __call__(self, request: Request) -> Optional[str | T]:
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
        try:
            model = self._model(**decoded_token)
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        self.extra_checks(model)
        return model


class OAuth2JWTBearer(OAuth2JWTBearerBase):
    _model = AccessTokenData

    def extra_checks(self, model):
        if model.type != TokenType.ACCESS:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


class OAuth2JWTBearerRefresh(OAuth2JWTBearerBase):
    _model = RefreshTokenData

    def extra_checks(self, model):
        if model.type != TokenType.REFRESH:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
