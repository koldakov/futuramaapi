from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.models import User as UserModel, UserDoesNotExist
from app.services.hashers import hasher
from app.services.security import (
    OAuth2PasswordRequestJson,
    TokenData,
    generate_jwt_signature,
)


class Token(BaseModel):
    access_token: str = Field(alias="accessToken")

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not hasher.verify(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return Token(
        access_token=generate_jwt_signature(
            TokenData(uuid=str(user.uuid)).model_dump(by_alias=True)
        )
    )
