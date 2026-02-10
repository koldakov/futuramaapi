from typing import Any, ClassVar

import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from pydantic import Field
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.core import settings
from futuramaapi.db.models import UserModel
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.routers.services import BaseSessionService, UnauthorizedError

from .get_auth_user_token import GetAuthUserTokenResponse


class GetRefreshedAuthUserTokenRequest(BaseModel):
    refresh_token: str = Field(
        alias="refresh_token",
    )


class GetRefreshedAuthUserTokenResponse(GetAuthUserTokenResponse):
    pass


class GetRefreshedAuthUserTokenService(BaseSessionService[GetRefreshedAuthUserTokenResponse]):
    request_data: GetRefreshedAuthUserTokenRequest

    algorithm: ClassVar[str] = "HS256"

    def __get_user_statement(self, decoded_token: dict[str, Any], /) -> Select[tuple[UserModel]]:
        return select(UserModel).where(UserModel.id == decoded_token["user"]["id"])

    async def _get_user(self, decoded_token: dict[str, Any], /) -> UserModel:
        result: Result[tuple[UserModel]] = await self.session.execute(self.__get_user_statement(decoded_token))
        try:
            user: UserModel = result.scalars().one()
        except NoResultFound:
            raise UnauthorizedError() from None

        return user

    async def process(self, *args, **kwargs) -> GetRefreshedAuthUserTokenResponse:
        try:
            decoded_token: dict[str, Any] = jwt.decode(
                self.request_data.refresh_token,
                key=settings.secret_key.get_secret_value(),
                algorithms=[self.algorithm],
            )
        except (ExpiredSignatureError, InvalidSignatureError, InvalidTokenError):
            raise UnauthorizedError() from None

        if decoded_token["type"] != "refresh":
            raise UnauthorizedError()

        user: UserModel = await self._get_user(decoded_token)

        return GetRefreshedAuthUserTokenResponse.from_user_model(user)
