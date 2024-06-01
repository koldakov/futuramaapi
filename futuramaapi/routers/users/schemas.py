from datetime import datetime
from typing import ClassVar, Self

from pydantic import EmailStr, Field, HttpUrl, SecretStr, field_validator, model_validator
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.core import feature_flags, settings
from futuramaapi.helpers.pydantic import BaseModel, BaseTokenModel
from futuramaapi.mixins.pydantic import BaseModelDatabaseMixin, BaseModelTokenMixin
from futuramaapi.repositories.base import ModelDoesNotExistError
from futuramaapi.repositories.models import UserModel
from futuramaapi.routers.exceptions import ModelNotFoundError


class UserBase(BaseModel):
    model: ClassVar[type[UserModel]] = UserModel

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


class UserCreateRequest(UserBase):
    @field_validator("password", mode="after")
    @classmethod
    def hash_password(cls, value: SecretStr, /) -> SecretStr:
        return SecretStr(cls.hasher.encode(value.get_secret_value()))


class UserBaseError(Exception): ...


class UserPasswordError(UserBaseError): ...


class UserAlreadyActivatedError(UserBaseError): ...


class UserUpdateRequest(BaseModel):
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
        min_length=1,
        max_length=64,
    )
    password: SecretStr | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )
    is_subscribed: bool | None = None

    @field_validator("password", mode="after")
    @classmethod
    def hash_password(cls, value: SecretStr | None, /) -> SecretStr | None:
        if value is None:
            return None
        return SecretStr(cls.hasher.encode(value.get_secret_value()))


class DecodedUserSignature(BaseTokenModel, BaseModelTokenMixin):
    id: int


class UserActivateRequest(BaseModel):
    is_confirmed: bool


class ConfirmationBody(BaseModel):
    class _User(BaseModel):
        id: int
        name: str
        surname: str

    user: _User
    url: HttpUrl = HttpUrl.build(
        scheme="https",
        host=settings.trusted_host,
    )

    @property
    def signature(self) -> str:
        return DecodedUserSignature(id=self.user.id).tokenize(3 * 24 * 60 * 60)

    @model_validator(mode="after")
    def build_confirmation_url(self) -> Self:
        self.url = HttpUrl.build(
            scheme=self.url.scheme,
            host=self.url.host,
            path="api/users/activate",
            query=f"sig={self.signature}",
        )
        return self

    @classmethod
    def from_user(cls, user: "User", /) -> Self:
        return cls(
            user=user.model_dump(),
        )


class User(UserBase, BaseModelDatabaseMixin):
    id: int
    is_confirmed: bool
    created_at: datetime

    def verify_password(self, password: str, /):
        if not self.hasher.verify(password, self.password.get_secret_value()):
            raise UserPasswordError() from None

    @classmethod
    async def from_username(cls, session: AsyncSession, username: str, /) -> Self:
        try:
            obj: UserModel = await cls.model.get(session, username, field=UserModel.username)
        except ModelDoesNotExistError:
            raise ModelNotFoundError() from None
        return cls.model_validate(obj)

    @classmethod
    async def auth(cls, session: AsyncSession, username: str, password: str, /) -> Self:
        try:
            user: User = await User.from_username(session, username)
        except ModelNotFoundError:
            raise

        try:
            user.verify_password(password)
        except UserPasswordError:
            raise

        return user

    async def activate(self, session: AsyncSession, /) -> None:
        if self.is_confirmed is True:
            raise UserAlreadyActivatedError() from None

        await self.update(session, UserActivateRequest(is_confirmed=True))

    async def send_confirmation_email(self) -> None:
        if self.is_confirmed is True:
            raise UserAlreadyActivatedError() from None

        if feature_flags.activate_users is False:
            return

        await settings.email.send(
            [self.email],
            "FuturamaAPI - Account Activation",
            ConfirmationBody.from_user(self),
            "emails/confirmation.html",
        )

    @classmethod
    async def create(cls, session: AsyncSession, data: BaseModel, /) -> Self:
        user: Self = await super().create(session, data)
        await user.send_confirmation_email()
        return user
