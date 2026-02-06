from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, TypeVar

import jwt
from fastapi_pagination import Page
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import UserModel
from futuramaapi.repositories.session import session_manager

TResponse = TypeVar(
    "TResponse",
    bound=BaseModel | Sequence[BaseModel] | Page[BaseModel] | None,
)


class ServiceError(Exception):
    """Service Error."""


class UnauthorizedError(ServiceError):
    """Unauthorized Error."""


class BaseService[TResponse](BaseModel, ABC):
    context: dict[str, Any] | None = None

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> TResponse:
        pass


class BaseSessionService[TResponse](BaseService[TResponse], ABC):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)

        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session is not initialized")

        return self._session

    @abstractmethod
    async def process(self, *args, **kwargs) -> TResponse: ...

    async def __call__(self, *args, **kwargs) -> TResponse:
        async with session_manager.session() as session:
            self._session = session

            return await self.process(*args, **kwargs)


class BaseUserAuthenticatedService[TResponse](BaseSessionService[TResponse], ABC):
    token: str

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)

        self._user: UserModel | None = None

    @property
    def user(self) -> UserModel:
        if self._user is None:
            raise RuntimeError("User is not initialized")

        return self._user

    def __get_decoded_token(
        self,
        *,
        algorithm="HS256",
    ) -> dict[str, Any]:
        try:
            decoded_token: dict[str, Any] = jwt.decode(
                self.token,
                key=settings.secret_key.get_secret_value(),
                algorithms=[algorithm],
            )
        except (ExpiredSignatureError, InvalidSignatureError, InvalidTokenError):
            raise UnauthorizedError() from None

        if decoded_token["type"] != "access":
            raise UnauthorizedError() from None

        return decoded_token

    @property
    def __get_user_statement(self) -> Select[tuple[UserModel]]:
        decoded_token: dict[str, Any] = self.__get_decoded_token()
        return select(UserModel).where(UserModel.id == decoded_token["user"]["id"])

    async def __set_user(self) -> None:
        try:
            self._user = (await self.session.execute(self.__get_user_statement)).scalars().one()
        except NoResultFound:
            raise UnauthorizedError() from None

    async def __call__(self, *args, **kwargs) -> TResponse:
        async with session_manager.session() as session:
            self._session = session
            await self.__set_user()

            return await self.process(*args, **kwargs)
