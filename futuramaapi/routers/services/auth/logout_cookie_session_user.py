from typing import ClassVar

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import Update, update

from futuramaapi.repositories.models import AuthSessionModel
from futuramaapi.routers.services import BaseSessionService


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
        key: str = self.request.cookies[self.cookie_auth_key]
        return update(AuthSessionModel).where(AuthSessionModel.key == key).values(expired=True)

    async def process(self, *args, **kwargs) -> RedirectResponse:
        await self.session.execute(self._expire_session_statement)
        await self.session.commit()

        response: RedirectResponse = RedirectResponse(
            "/auth",
            status_code=status.HTTP_302_FOUND,
        )
        response.delete_cookie(self.cookie_auth_key)
        return response
