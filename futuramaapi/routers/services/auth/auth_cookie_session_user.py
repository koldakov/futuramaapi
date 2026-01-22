from typing import ClassVar

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from pydantic import SecretStr
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.repositories.models import AuthSessionModel, UserModel
from futuramaapi.routers.services import BaseSessionService


class AuthCookieSessionUserService(BaseSessionService[RedirectResponse]):
    username: str
    password: SecretStr

    cookie_auth_key: ClassVar[str] = "Authorization"

    @property
    def request(self) -> Request:
        if self.context is None:
            raise AttributeError("Request is not defined.")

        if "request" not in self.context:
            raise AttributeError("Request is not defined.")

        return self.context["request"]

    @property
    def __get_user_statement(self) -> Select[tuple[UserModel]]:
        return select(UserModel).where(UserModel.username == self.username)

    async def _get_user(self) -> UserModel:
        result: Result[tuple[UserModel]] = await self.session.execute(self.__get_user_statement)
        try:
            return result.scalars().one()
        except NoResultFound:
            raise

    async def _get_auth_session(self, user: UserModel, /) -> AuthSessionModel:
        auth_session: AuthSessionModel = AuthSessionModel()
        auth_session.user_id = user.id
        auth_session.ip_address = self.request.client.host

        self.session.add(auth_session)
        await self.session.commit()

        return auth_session

    def _build_response(self, auth_session: AuthSessionModel, /) -> RedirectResponse:
        response: RedirectResponse = RedirectResponse(
            "/",
            status_code=status.HTTP_302_FOUND,
        )
        response.set_cookie(
            self.cookie_auth_key,
            value=auth_session.key,
            expires=AuthSessionModel.cookie_expiration_time,
        )
        return response

    async def process(self, *args, **kwargs) -> RedirectResponse:
        try:
            user: UserModel = await self._get_user()
        except NoResultFound:
            return RedirectResponse(
                url="/auth",
                status_code=status.HTTP_302_FOUND,
            )

        if not self.hasher.verify(self.password.get_secret_value(), user.password):
            return RedirectResponse(
                url="/auth",
                status_code=status.HTTP_302_FOUND,
            )

        auth_session: AuthSessionModel = await self._get_auth_session(user)
        return self._build_response(auth_session)
