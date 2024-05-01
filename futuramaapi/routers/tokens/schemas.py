from typing import TYPE_CHECKING, ClassVar, Literal, Self

from pydantic import Field

from futuramaapi.helpers.pydantic import BaseModel, BaseTokenModel
from futuramaapi.mixins.pydantic import BaseModelTokenMixin, DecodedTokenError

if TYPE_CHECKING:
    from futuramaapi.routers.users.schemas import User


class _DecodedTokenBase(BaseTokenModel):
    type: Literal["access", "refresh"]


class DecodedUserToken(_DecodedTokenBase, BaseModelTokenMixin):
    id: int

    @classmethod
    def from_user(cls, user: "User", type_: Literal["access", "refresh"], /) -> Self:
        return cls(type=type_, **user.model_dump())

    @classmethod
    def decode(
        cls,
        token: str,
        /,
        *,
        algorithm="HS256",
        allowed_type: Literal["access", "refresh"] = "access",
    ) -> Self:
        decoded_token: Self = super().decode(token, algorithm=algorithm)
        if decoded_token.type != allowed_type:
            raise DecodedTokenError() from None

        return decoded_token


class UserTokenRefreshRequest(BaseModel):
    refresh_token: str


class UserToken(BaseModel):
    access_token: str = Field(
        alias="access_token",
        description="Keep in mind, that the field is not in a camel case. That's the standard.",
    )
    refresh_token: str = Field(
        alias="refresh_token",
        description="Keep in mind, that the field is not in a camel case. That's the standard.",
    )

    _default_access_seconds: ClassVar[int] = 15 * 60
    _default_refresh_seconds: ClassVar[int] = 5 * 24 * 60 * 60

    @classmethod
    def from_user(
        cls,
        user: "User",
        /,
    ) -> Self:
        access: DecodedUserToken = DecodedUserToken.from_user(user, "access")
        refresh: DecodedUserToken = DecodedUserToken.from_user(user, "refresh")
        return cls(
            access_token=access.tokenize(cls._default_access_seconds),
            refresh_token=refresh.tokenize(cls._default_refresh_seconds),
        )

    def refresh(self) -> None:
        try:
            access: DecodedUserToken = DecodedUserToken.decode(self.access_token)
        except DecodedTokenError:
            raise

        try:
            refresh: DecodedUserToken = DecodedUserToken.decode(self.refresh_token, allowed_type="refresh")
        except DecodedTokenError:
            raise

        access.refresh_nonce()
        refresh.refresh_nonce()

        self.access_token = access.tokenize(self._default_access_seconds)
        self.refresh_token = refresh.tokenize(self._default_refresh_seconds)
