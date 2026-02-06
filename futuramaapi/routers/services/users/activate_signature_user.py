from typing import Any, ClassVar

import jwt
from fastapi import Request, status
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from sqlalchemy import Result, Select, Update, select, update
from starlette.responses import RedirectResponse

from futuramaapi.core import settings
from futuramaapi.repositories.models import UserModel
from futuramaapi.routers.services import BaseSessionService, UnauthorizedError


class TokenDecodeError(Exception):
    pass


class ActivateSignatureUserService(BaseSessionService[RedirectResponse]):
    signature: str

    algorithm: ClassVar[str] = "HS256"

    @property
    def request(self) -> Request:
        if self.context is None:
            raise AttributeError("Request is not defined.")

        if "request" not in self.context:
            raise AttributeError("Request is not defined.")

        return self.context["request"]

    def _get_decoded_token(self) -> dict[str, Any]:
        try:
            token_: dict = jwt.decode(
                self.signature,
                key=settings.secret_key.get_secret_value(),
                algorithms=[self.algorithm],
            )
        except (ExpiredSignatureError, InvalidSignatureError, InvalidTokenError):
            raise TokenDecodeError() from None

        if token_["type"] != "access":
            raise TokenDecodeError() from None

        return token_

    def __get_user_statement(self, pk: int, /) -> Select[tuple[UserModel]]:
        return select(UserModel).where(UserModel.id == pk)

    async def _get_current_user(self, pk: int, /) -> UserModel:
        result: Result[tuple[UserModel]] = await self.session.execute(self.__get_user_statement(pk))
        return result.scalars().one()

    def __get_update_user_statement(self, pk: int, /) -> Update:
        return update(UserModel).where(UserModel.id == pk).values(is_confirmed=True)

    async def process(self, *args, **kwargs) -> RedirectResponse:
        try:
            token_: dict[str, Any] = self._get_decoded_token()
        except TokenDecodeError:
            raise UnauthorizedError("Token expired or invalid.") from None

        user: UserModel = await self._get_current_user(token_["user"]["id"])

        if user.is_confirmed:
            raise UnauthorizedError("User already activated.")

        await self.session.execute(self.__get_update_user_statement(user.id))
        await self.session.commit()

        return RedirectResponse(
            url="/auth",
            status_code=status.HTTP_302_FOUND,
        )
