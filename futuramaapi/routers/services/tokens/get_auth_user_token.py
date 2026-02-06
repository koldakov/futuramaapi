import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, ClassVar, Self

import jwt
from pydantic import Field, SecretStr
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import UserModel
from futuramaapi.routers.services import BaseSessionService, UnauthorizedError


class GetAuthUserTokenResponse(BaseModel):
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
    def from_user_model(
        cls,
        user: UserModel,
        /,
        *,
        algorithm="HS256",
    ) -> Self:
        return cls(
            access_token=jwt.encode(
                {
                    "exp": datetime.now(UTC) + timedelta(seconds=cls._default_access_seconds),
                    "nonce": uuid.uuid4().hex,
                    "type": "access",
                    "user": {
                        "id": user.id,
                    },
                },
                settings.secret_key.get_secret_value(),
                algorithm=algorithm,
            ),
            refresh_token=jwt.encode(
                {
                    "exp": datetime.now(UTC) + timedelta(seconds=cls._default_refresh_seconds),
                    "nonce": uuid.uuid4().hex,
                    "type": "refresh",
                    "user": {
                        "id": user.id,
                    },
                },
                settings.secret_key.get_secret_value(),
                algorithm=algorithm,
            ),
        )


class GetAuthUserTokenService(BaseSessionService[GetAuthUserTokenResponse]):
    username: str
    password: SecretStr

    @property
    def __user_statement(self) -> Select[tuple[UserModel]]:
        return select(UserModel).where(UserModel.username == self.username)

    async def _get_user(self) -> UserModel:
        result: Result[tuple[Any]] = await self.session.execute(self.__user_statement)
        try:
            return result.scalars().one()
        except NoResultFound:
            raise UnauthorizedError() from None

    async def process(self, *args, **kwargs) -> GetAuthUserTokenResponse:
        user: UserModel = await self._get_user()
        if not self.hasher.verify(self.password.get_secret_value(), user.password):
            raise UnauthorizedError()

        return GetAuthUserTokenResponse.from_user_model(user)
