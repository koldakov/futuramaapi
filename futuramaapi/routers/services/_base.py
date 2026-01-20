from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, ClassVar, TypeVar

from fastapi import HTTPException, Request, status
from fastapi_pagination import Page
from pydantic import Field
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.templating import _TemplateResponse

from futuramaapi.__version__ import __version__
from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.helpers.templates import templates
from futuramaapi.mixins.pydantic import DecodedTokenError
from futuramaapi.repositories.models import AuthSessionModel, UserModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.rest.tokens.schemas import DecodedUserToken
from futuramaapi.utils import config, metadata

TResponse = TypeVar(
    "TResponse",
    bound=BaseModel | Sequence[BaseModel] | Page[BaseModel] | None,
)


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


class _ProjectContext(BaseModel):
    version: str = Field(
        default=__version__,
    )
    g_tag: str = Field(
        default=settings.g_tag,
        alias="G_TAG",
    )
    author: str | None = Field(
        default=metadata.get("author", None),
    )
    description: str = Field(
        default=metadata["summary"],
    )
    config: dict[str, Any] = config


_project_context: _ProjectContext = _ProjectContext()


class BaseTemplateService(BaseSessionService[_TemplateResponse], ABC):
    template_name: ClassVar[str]

    _cookie_auth_key: ClassVar[str] = "Authorization"

    @abstractmethod
    async def get_context(self, *args, **kwargs) -> dict[str, Any]: ...

    @property
    def request(self) -> Request:
        if self.context is None:
            raise AttributeError("Request is not defined.")

        if "request" not in self.context:
            raise AttributeError("Request is not defined.")

        return self.context["request"]

    @property
    def __auth_session_statement(self) -> Select[tuple[AuthSessionModel]]:
        statement: Select[tuple[AuthSessionModel]] = select(AuthSessionModel)
        statement = statement.where(AuthSessionModel.key == self.request.cookies[self._cookie_auth_key])
        statement = statement.options(selectinload(AuthSessionModel.user))
        return statement

    async def _get_current_user(self) -> UserModel | None:
        if self._cookie_auth_key not in self.request.cookies:
            return None

        result: Result[tuple[AuthSessionModel]] = await self.session.execute(self.__auth_session_statement)
        try:
            auth_session: AuthSessionModel = result.scalars().one()
        except NoResultFound:
            return None

        if not auth_session.valid:
            return None

        return auth_session.user

    async def _get_context(self) -> dict[str, Any]:
        context: dict[str, Any] = await self.get_context()
        context["_project"] = _project_context
        context["current_user"] = await self._get_current_user()
        return context

    async def process(self, *args, **kwargs) -> _TemplateResponse:
        return templates.TemplateResponse(
            self.request,
            self.template_name,
            context=await self._get_context(),
        )


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

    @property
    def __get_user_statement(self) -> Select[tuple[UserModel]]:
        try:
            decoded_token: DecodedUserToken = DecodedUserToken.decode(self.token, allowed_type="access")
        except DecodedTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

        return select(UserModel).where(UserModel.id == decoded_token.user.id)

    async def __set_user(self) -> None:
        try:
            self._user = (await self.session.execute(self.__get_user_statement)).scalars().one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    async def __call__(self, *args, **kwargs) -> TResponse:
        async with session_manager.session() as session:
            self._session = session
            await self.__set_user()

            return await self.process(*args, **kwargs)
