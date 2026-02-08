from pydantic import Field, SecretStr, field_validator

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.routers.services import BaseUserAuthenticatedService, EmptyUpdateError

from .get_user_me import GetUserMeResponse


class UpdateUserRequest(BaseModel):
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


class UpdateUserResponse(GetUserMeResponse):
    pass


class UpdateUserService(BaseUserAuthenticatedService[UpdateUserResponse]):
    request_data: UpdateUserRequest

    async def process(self, *args, **kwargs) -> UpdateUserResponse:
        data: dict[str, str] = self.request_data.to_dict(by_alias=False, reveal_secrets=True, exclude_unset=True)
        if not data:
            raise EmptyUpdateError()

        for field, value in data.items():
            setattr(self.user, field, value)

        self.session.add(self.user)
        await self.session.commit()

        return UpdateUserResponse.model_validate(self.user)
