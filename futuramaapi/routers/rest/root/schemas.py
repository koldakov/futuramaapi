from pathlib import Path
from typing import ClassVar, Self

import aiofiles
from aiocache import Cache, cached
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from futuramaapi.core import settings
from futuramaapi.helpers import render_markdown
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.mixins.pydantic import BaseModelTemplateMixin, ProjectContext


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
