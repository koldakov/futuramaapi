from json import loads
from uuid import uuid4

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.models import User as UserModel
from app.repositories.models import UserDoesNotExist
from app.services.hashers import hasher
from app.services.security import (
    REFRESH_JWT_EXPIRATION_TIME,
    AccessTokenData,
    OAuth2PasswordRequestJson,
    RefreshTokenData,
    generate_jwt_signature,
)


class Token(BaseModel):
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None
    if not hasher.verify(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    return Token(
        access_token=generate_jwt_signature(
            loads(
                AccessTokenData(uuid=user.uuid).model_dump_json(by_alias=True),
            ),
        ),
        refresh_token=generate_jwt_signature(
            loads(
                RefreshTokenData(
                    uuid=user.uuid,
                    nonce=uuid4().hex,
                ).model_dump_json(by_alias=True)
            ),
            expiration_time=REFRESH_JWT_EXPIRATION_TIME,
        ),
    )


class RefreshToken(BaseModel):
    access_token: str


async def process_refresh_token_auth_user(data: RefreshTokenData) -> RefreshToken:
    return RefreshToken(
        access_token=generate_jwt_signature(
            loads(
                AccessTokenData(**data.model_dump()).model_dump_json(by_alias=True),
            ),
        )
    )
