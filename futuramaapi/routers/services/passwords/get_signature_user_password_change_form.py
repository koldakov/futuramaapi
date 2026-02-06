from enum import StrEnum
from typing import Any, ClassVar

import jwt
from fastapi import Request, Response
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from sqlalchemy import Result, Select, select

from futuramaapi.core import settings
from futuramaapi.helpers.templates import templates
from futuramaapi.repositories.models import UserModel
from futuramaapi.routers.services import BaseSessionService
from futuramaapi.routers.services._base_template import _project_context


class TokenDecodeError(Exception):
    pass


class ChangeFormError(StrEnum):
    password_mismatch = "password_mismatch"  # noqa: S105


class GetSignatureUserPasswordChangeFormService(BaseSessionService[Response]):
    template_name: ClassVar[str] = "password_change.html"

    signature: str
    error_type: ChangeFormError | None

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

    async def _get_context(self, token: dict[str, Any], /) -> dict[str, Any]:
        return {
            "_project": _project_context,
            "current_user": await self._get_current_user(token["user"]["id"]),
            "error_type": self.error_type,
        }

    async def process(self, *args, **kwargs) -> Response:
        try:
            token_: dict[str, Any] = self._get_decoded_token()
        except TokenDecodeError:
            return templates.TemplateResponse(
                self.request,
                self.template_name,
                context={
                    "_project": _project_context,
                    "current_user": None,
                },
            )

        return templates.TemplateResponse(
            self.request,
            self.template_name,
            context=await self._get_context(token_),
        )
