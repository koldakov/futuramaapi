from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Self

import aiofiles
from aiocache import Cache, cached
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from futuramaapi.core import settings
from futuramaapi.helpers import render_markdown
from futuramaapi.helpers.pydantic import BaseModel, Field
from futuramaapi.mixins.pydantic import BaseModelTemplateMixin, ProjectContext
from futuramaapi.repositories import FilterStatementKwargs
from futuramaapi.repositories.models import CharacterModel, RequestsCounterModel, SystemMessage
from futuramaapi.routers.rest.users.schemas import User
from futuramaapi.routers.services.characters.get_character import GetCharacterResponse

if TYPE_CHECKING:
    from collections.abc import Sequence


class Root(BaseModel, BaseModelTemplateMixin):
    characters: list[GetCharacterResponse]
    user_count: int = Field(alias="user_count")
    total_api_requests: int
    last_day_api_requests: int
    system_messages: list[str]

    template_name: ClassVar[str] = "index.html"

    @classmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self:
        user_count: int = await User.count(session)
        statement: Select[tuple[CharacterModel]] = select(CharacterModel).limit(12).order_by(CharacterModel.id.asc())
        characters: Sequence[CharacterModel] = (await session.execute(statement)).scalars().all()
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


@cached(
    ttl=None,
    cache=Cache.MEMORY,
)
async def _get_rendered_content() -> str:
    path: Path = Path(settings.project_root) / "CHANGELOG.md"
    async with aiofiles.open(path, encoding="utf-8") as f:
        raw_content = await f.read()
    return render_markdown(raw_content)


class Changelog(BaseModel, BaseModelTemplateMixin):
    content: str

    template_name: ClassVar[str] = "changelog.html"

    @classmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self:
        return cls(
            content=await _get_rendered_content(),
        )
