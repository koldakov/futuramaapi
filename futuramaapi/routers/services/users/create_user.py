import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, ClassVar

import jwt
from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from pydantic import EmailStr, Field, HttpUrl, SecretStr, field_validator
from sqlalchemy import exc

from futuramaapi.core import feature_flags, settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import UserModel
from futuramaapi.routers.services import BaseSessionService

from .get_user_me import GetUserMeResponse


class CreateUserRequest(BaseModel):
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
        min_length=1,
        max_length=64,
    )
    email: EmailStr
    username: str = Field(
        min_length=5,
        max_length=64,
    )
    password: SecretStr = Field(
        min_length=8,
        max_length=128,
    )
    is_subscribed: bool = Field(
        default=True,
    )

    @field_validator("password", mode="after")
    @classmethod
    def hash_password(cls, value: SecretStr, /) -> SecretStr:
        return SecretStr(cls.hasher.encode(value.get_secret_value()))


class CreateUserResponse(GetUserMeResponse):
    pass


class CreateUserService(BaseSessionService[CreateUserResponse]):
    request_data: CreateUserRequest

    expiration_time: ClassVar[int] = 3 * 24 * 60 * 60

    def _get_signature(
        self,
        user: UserModel,
        /,
        *,
        algorithm: str = "HS256",
    ) -> str:
        return jwt.encode(
            {
                "exp": datetime.now(UTC) + timedelta(seconds=self.expiration_time),
                "nonce": uuid.uuid4().hex,
                "type": "access",
                "user": {
                    "id": user.id,
                },
            },
            settings.secret_key.get_secret_value(),
            algorithm=algorithm,
        )

    def _get_confirmation_url(self, user: UserModel, /) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme="https",
            host=settings.trusted_host,
            path="users/activate",
            query=f"sig={self._get_signature(user)}",
        )
        return str(url)

    def _get_template_body(self, user: UserModel, /) -> dict[str, Any]:
        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
            },
            "url": self._get_confirmation_url(user),
        }

    async def _send_confirmation_email(self, user: UserModel, /) -> None:
        if not feature_flags.activate_users:
            return

        await settings.email.send(
            [user.email],
            "FuturamaAPI - Account Activation",
            self._get_template_body(user),
            "emails/confirmation.html",
        )

    def _get_user(self) -> UserModel:
        return UserModel(
            **self.request_data.to_dict(
                by_alias=False,
                reveal_secrets=True,
                exclude_unset=True,
            )
        )

    async def process(self, *args, **kwargs) -> CreateUserResponse:
        user: UserModel = self._get_user()
        self.session.add(user)

        try:
            await self.session.commit()
        except exc.IntegrityError as err:
            if err.orig.sqlstate == UniqueViolationError.sqlstate:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User already exists.",
                ) from None
            raise

        await self._send_confirmation_email(user)

        return CreateUserResponse.model_validate(user)
