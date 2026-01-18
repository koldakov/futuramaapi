from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from pydantic import EmailStr, Field, SecretStr
from sqlalchemy import exc

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


class CreateUserResponse(GetUserMeResponse):
    pass


class CreateUserService(BaseSessionService[CreateUserResponse]):
    request_data: CreateUserRequest

    def _get_user(self) -> UserModel:
        return UserModel(
            **self.request_data.to_dict(
                by_alias=False,
                reveal_secrets=True,
                exclude_unset=True,
            )
        )

    async def process(self, *args, **kwargs) -> CreateUserResponse:
        user_model: UserModel = self._get_user()
        self.session.add(user_model)

        try:
            await self.session.commit()
        except exc.IntegrityError as err:
            if err.orig.sqlstate == UniqueViolationError.sqlstate:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User already exists.",
                ) from None
            raise

        return CreateUserResponse.model_validate(user_model)
