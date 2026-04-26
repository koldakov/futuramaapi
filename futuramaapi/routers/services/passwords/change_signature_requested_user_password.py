import re
from typing import Any, ClassVar

import jwt
from fastapi import Request, status
from fastapi.responses import RedirectResponse
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from pydantic import Field, SecretStr, field_validator
from sqlalchemy import Update, update

from futuramaapi.core import settings
from futuramaapi.db.models import UserModel
from futuramaapi.routers.services import BaseSessionService
from futuramaapi.routers.services.auth.get_user_auth import UserAuthMessageType

from .get_signature_user_password_change_form import ChangeFormError


class TokenDecodeError(Exception):
    pass


class ChangeSignatureRequestedUserPasswordService(BaseSessionService[RedirectResponse]):
    password1: SecretStr = Field(
        min_length=8,
        max_length=128,
    )
    password2: SecretStr = Field(
        min_length=8,
        max_length=128,
    )
    signature: str

    @field_validator("password1", "password2")
    @classmethod
    def validate_password_strength(cls, v: SecretStr) -> SecretStr:
        """Validate password has 8+ chars with letters and numbers."""
        password_str = v.get_secret_value()
        if not re.match(r"(?=.*[A-Za-z])(?=.*\d).{8,}", password_str):
            raise ValueError("Password must contain at least 8 characters with letters and numbers")
        return v

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
            return RedirectResponse(
                url=f"/passwords/change?sig={self.signature}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        if self.password1.get_secret_value() != self.password2.get_secret_value():
            return RedirectResponse(
                url=f"/passwords/change?sig={self.signature}&errorType={ChangeFormError.password_mismatch}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        await self.session.execute(self._get_update_user_password_statement(token_["user"]["id"]))
        await self.session.commit()

        return RedirectResponse(
            url=f"/auth?messageType={UserAuthMessageType.password_changed}",
            status_code=status.HTTP_302_FOUND,
        )
