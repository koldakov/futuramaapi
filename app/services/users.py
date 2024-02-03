from datetime import datetime
from gettext import gettext as _
from json import dumps, loads
from typing import Dict
from urllib.parse import urlencode
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.configs import feature_flags, settings
from app.repositories.models import (
    User as UserModel,
    UserAlreadyExists,
    UserDoesNotExist,
)
from app.services.emails import ConfirmationBody, send_confirmation
from app.services.hashers import hasher
from app.services.security import (
    AccessTokenData,
    FatalSignatureError,
    SignatureExpiredError,
    decode_jwt_signature,
    generate_jwt_signature,
)


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


class PasswordHashMixin:
    @field_validator("password", mode="before")
    @classmethod
    def hash_password(cls, value: str) -> str:
        return hasher.encode(value)


class UserAdd(UserBase, PasswordHashMixin):
    ...


class User(UserBase):
    id: int
    is_confirmed: bool = Field(alias="isConfirmed")
    created_at: datetime = Field(alias="createdAt")


EXPIRATION_72_HOURS = 60 * 60 * 72


def _get_signature(uuid: UUID):
    return generate_jwt_signature(
        loads(
            dumps(
                {
                    "uuid": uuid,
                },
                default=str,
            )
        ),
        expiration_time=EXPIRATION_72_HOURS,
    )


def get_confirmation_body(user: UserModel, /) -> ConfirmationBody:
    url = HttpUrl.build(
        scheme="https",
        host=settings.trusted_host,
        path="api/users/activate",
        query=urlencode(
            {
                "sig": _get_signature(user.uuid),
            }
        ),
    )
    return ConfirmationBody(
        url=url,
        user={
            "name": user.name,
            "surname": user.surname,
        },
    )


async def process_add_user(body: UserAdd, session: AsyncSession, /) -> User:
    try:
        user: UserModel = await UserModel.add(session, body)
    except UserAlreadyExists:
        raise HTTPException(
            detail="User with username or email already exists",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if feature_flags.activate_users:
        await send_confirmation(
            [user.email],
            _("FuturamaAPI - Account Activation"),
            get_confirmation_body(user),
        )
    return User.model_validate(user)


async def process_get_me(token: AccessTokenData, session: AsyncSession, /) -> User:
    try:
        user: UserModel = await UserModel.get(session, token.uuid, field=UserModel.uuid)
    except UserDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return User.model_validate(user)


def _get_uuid(signature: str, /) -> UUID:
    try:
        decoded_signature = decode_jwt_signature(signature)
    except SignatureExpiredError:
        raise HTTPException(
            detail="Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except FatalSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        uuid = decoded_signature["uuid"]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return UUID(uuid)


async def process_activate(signature: str, session: AsyncSession, /) -> User:
    uuid = _get_uuid(signature)
    try:
        user: UserModel = await UserModel.get(session, uuid, field=UserModel.uuid)
    except UserDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if user.is_confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user.is_confirmed = True
    await session.commit()

    return User.model_validate(user)


class UserUpdate(BaseModel, PasswordHashMixin):
    name: str | None = Field(
        min_length=1,
        max_length=64,
        default=None,
    )
    surname: str | None = Field(
        min_length=1,
        max_length=64,
        default=None,
    )
    middle_name: str | None = Field(
        default=None,
        alias="middleName",
        min_length=1,
        max_length=64,
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )
    is_subscribed: bool | None = Field(
        default=None,
        alias="isSubscribed",
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


async def process_update(
    token: AccessTokenData,
    request_user: UserUpdate,
    session: AsyncSession,
    /,
) -> User:
    request_user_dict: Dict = request_user.model_dump(exclude_none=True)
    if not request_user_dict:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        user: UserModel = await UserModel.get(session, token.uuid, field=UserModel.uuid)
    except UserDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    for field, value in request_user_dict.items():
        setattr(user, field, value)
    await session.commit()
    return user
