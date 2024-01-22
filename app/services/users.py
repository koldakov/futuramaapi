from datetime import datetime

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.models import User as UserModel, UserAlreadyExists
from app.services.hashers import hasher


class UserBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=64,
    )
    surname: str = Field(
        min_length=1,
        max_length=64,
    )
    middle_name: str | None = Field(
        default=None,
        alias="middleName",
        min_length=1,
        max_length=64,
    )
    email: EmailStr
    username: str = Field(
        min_length=5,
        max_length=64,
    )
    password: str = Field(
        min_length=8,
        max_length=128,
    )
    is_subscribed: bool = Field(
        default=True,
        alias="isSubscribed",
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class UserAdd(UserBase):
    ...


class User(UserBase):
    id: int
    is_confirmed: bool = Field(alias="isConfirmed")
    created_at: datetime = Field(alias="createdAt")


async def process_add_user(body: UserAdd, session: AsyncSession, /):
    body.password = hasher.encode(body.password)
    try:
        user: UserModel = await UserModel.add(session, body)
    except UserAlreadyExists:
        raise HTTPException(
            detail="User with username or email already exists",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return User.model_validate(user)