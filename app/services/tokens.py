from copy import deepcopy
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException, status
from jose import exceptions, jwt
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.configs import settings
from app.repositories.models import User as UserModel, UserDoesNotExist
from app.services.hashers import hasher
from app.services.security import OAuth2PasswordRequestJson

DEFAULT_JWT_EXPIRATION_TIME: int = 15 * 60


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
):
    if algorithms is None:
        algorithms = ["HS256"]

    try:
        return jwt.decode(token, settings.secret_key, algorithms=algorithms)
    except (exceptions.JWSError, exceptions.JWSSignatureError):
        raise FatalSignatureError()
    except exceptions.ExpiredSignatureError:
        raise SignatureExpiredError()


class Token(BaseModel):
    access_token: str = Field(alias="accessToken")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TokenData(BaseModel):
    uuid: str


async def process_token_auth_user(
    session: AsyncSession,
    data: OAuth2PasswordRequestJson,
    /,
) -> Token:
    try:
        user: UserModel = await UserModel.get(
            session,
            data.username,
            field=UserModel.username,
        )
    except UserDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not hasher.verify(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return Token(
        access_token=generate_jwt_signature(
            TokenData(uuid=str(user.uuid)).model_dump(by_alias=True)
        )
    )
