from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, ClassVar, Self

from fastapi import Response
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel, Field
from futuramaapi.mixins.pydantic import BaseModelTemplateMixin, ProjectContext
from futuramaapi.repositories import FilterStatementKwargs
from futuramaapi.repositories.models import RequestsCounterModel, SystemMessage
from futuramaapi.routers.rest.characters.schemas import Character
from futuramaapi.routers.rest.users.schemas import User

if TYPE_CHECKING:
    from collections.abc import Sequence


class Root(BaseModel, BaseModelTemplateMixin):
    characters: list[Character]
    user_count: int = Field(alias="user_count")
    total_api_requests: int
    last_day_api_requests: int
    system_messages: list[str]

    template_name: ClassVar[str] = "index.html"

    @classmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self:
        user_count: int = await User.count(session)
        characters: list[Character] = await Character.filter(
            session,
            FilterStatementKwargs(
                limit=6,
            ),
        )
        total_requests: int = await RequestsCounterModel.get_total_requests()
        system_messages: Sequence[SystemMessage] = await SystemMessage.filter(session, FilterStatementKwargs())
        last_day_api_requests: int = await RequestsCounterModel.get_requests_since(
            datetime.now(tz=UTC) - timedelta(days=1),
        )

        return cls(
            characters=characters,
            user_count=user_count,
            total_api_requests=total_requests,
            last_day_api_requests=last_day_api_requests,
            system_messages=[system_message.message for system_message in system_messages],
        )


class About(BaseModel, BaseModelTemplateMixin):
    template_name: ClassVar[str] = "about.html"

    @property
    def project_context(self) -> ProjectContext:
        return ProjectContext(
            description="Practice with API, learn to code, and gain hands-on experience with SSE, callbacks, and more.",
        )

    @classmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self:
        return cls()


class UserAuth(BaseModel, BaseModelTemplateMixin):
    template_name: ClassVar[str] = "auth.html"

    @property
    def project_context(self) -> ProjectContext:
        return ProjectContext(
            description="Log in to your Futurama API account to manage your account and access all your tools "
            "securely and easily.",
        )

    @classmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self:
        return cls()


class SiteMap(BaseModel):
    _header: ClassVar[str] = '<?xml version="1.0" encoding="UTF-8"?>'
    _media_type: ClassVar[str] = "application/xml"
    _url_tag: ClassVar[str] = """<url><loc>%s</loc></url>"""
    _url_set_tag: ClassVar[str] = """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>"""

    base_url: HttpUrl = settings.build_url(is_static=False)
    urls: list[str]

    async def get_response(self) -> Response:
        urls: str = ""
        for url in self.urls:
            urls += self._url_tag % settings.build_url(
                path=url,
                is_static=False,
            )
        url_set: str = self._url_set_tag % urls
        return Response(
            content=f"""{self._header}{url_set}""",
            media_type=self._media_type,
        )

    @classmethod
    async def from_request(cls, request: Request) -> Self:
        from futuramaapi.apps import app

        return cls(
            urls=[url.path for url in app.public_urls],
        )
