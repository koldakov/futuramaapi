from typing import ClassVar

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import Update, update

from futuramaapi.db.models import AuthSessionModel
from futuramaapi.routers.services import BaseSessionService


class CookieAuthKeyIsNotDefinedError(Exception): ...


class LogoutCookieSessionUserService(BaseSessionService[RedirectResponse]):
    cookie_auth_key: ClassVar[str] = "Authorization"

    @property
    def request(self) -> Request:
        if self.context is None:
            raise AttributeError("Request is not defined.")

        if "request" not in self.context:
            raise AttributeError("Request is not defined.")

        return self.context["request"]

    @property
    def _expire_session_statement(self) -> Update:
        try:
            key: str = self.request.cookies[self.cookie_auth_key]
        except KeyError:
            raise CookieAuthKeyIsNotDefinedError() from None

        return update(AuthSessionModel).where(AuthSessionModel.key == key).values(expired=True)

    async def process(self, *args, **kwargs) -> RedirectResponse:
        try:
            await self.session.execute(self._expire_session_statement)
        except CookieAuthKeyIsNotDefinedError:
            return RedirectResponse(
                "/auth",
                status_code=status.HTTP_302_FOUND,
            )

        await self.session.commit()

        response: RedirectResponse = RedirectResponse(
            "/auth",
            status_code=status.HTTP_302_FOUND,
        )
        response.delete_cookie(self.cookie_auth_key)
        return response
