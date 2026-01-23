from typing import TYPE_CHECKING, Literal, Self

from futuramaapi.helpers.pydantic import BaseModel, BaseTokenModel
from futuramaapi.mixins.pydantic import BaseModelTokenMixin, DecodedTokenError

if TYPE_CHECKING:
    from futuramaapi.routers.rest.users.schemas import User


class _DecodedTokenBase(BaseTokenModel):
    type: Literal["access", "refresh"]


class DecodedUserToken(_DecodedTokenBase, BaseModelTokenMixin):
    class _User(BaseModel):
        id: int

    user: _User

    @classmethod
    def from_user(cls, user: "User", type_: Literal["access", "refresh"], /) -> Self:
        return cls(type=type_, user=user.model_dump())

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
