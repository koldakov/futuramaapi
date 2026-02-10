from abc import ABC, abstractmethod
from typing import Any, ClassVar

from fastapi import Request
from pydantic import Field
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload
from starlette.templating import _TemplateResponse

from futuramaapi.__version__ import __version__
from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.helpers.templates import templates
from futuramaapi.repositories.models import AuthSessionModel, UserModel
from futuramaapi.utils import config, metadata

from ._base import BaseSessionService


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
    """
    Base service for rendering templates with a populated request context.

    Attributes:
        template_name: Name of the template to render. Must be set in subclasses.
    """

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
        return (
            select(AuthSessionModel)
            .where(AuthSessionModel.key == self.request.cookies[self._cookie_auth_key])
            .options(selectinload(AuthSessionModel.user))
        )

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
