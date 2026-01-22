from typing import Any, ClassVar

import jwt
from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from pydantic import SecretStr
from sqlalchemy import Update, update

from futuramaapi.core import settings
from futuramaapi.repositories.models import UserModel
from futuramaapi.routers.services import BaseSessionService


class TokenDecodeError(Exception):
    pass


class ChangeSignatureRequestedUserPasswordService(BaseSessionService[RedirectResponse]):
    password1: SecretStr
    password2: SecretStr
    signature: str

    algorithm: ClassVar[str] = "HS256"

    @property
    def request(self) -> Request:
        if self.context is None:
            raise AttributeError("Request is not defined.")

        if "request" not in self.context:
            raise AttributeError("Request is not defined.")

        return self.context["request"]

    def _get_update_user_password_statement(self, pk: int, /) -> Update:
        password: str = self.hasher.encode(self.password1.get_secret_value())
        return update(UserModel).where(UserModel.id == pk).values(is_confirmed=True, password=password)

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

    async def process(self, *args, **kwargs) -> RedirectResponse:
        try:
            token_: dict[str, Any] = self._get_decoded_token()
        except TokenDecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or invalid.",
            ) from None

        if self.password1.get_secret_value() != self.password2.get_secret_value():
            return RedirectResponse(
                self.request.headers.get("referer", self.request.url.path),
                status_code=status.HTTP_303_SEE_OTHER,
            )

        await self.session.execute(self._get_update_user_password_statement(token_["user"]["id"]))
        await self.session.commit()

        return RedirectResponse(
            url="/auth",
            status_code=status.HTTP_302_FOUND,
        )
