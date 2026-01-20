from pathlib import Path
from typing import Any

import aiofiles
from aiocache import Cache, cached

from futuramaapi.core import settings
from futuramaapi.helpers import render_markdown
from futuramaapi.routers.services import BaseTemplateService


@cached(
    ttl=None,
    cache=Cache.MEMORY,
)
async def _get_rendered_content() -> str:
    path: Path = Path(settings.project_root) / "CHANGELOG.md"
    async with aiofiles.open(path, encoding="utf-8") as f:
        raw_content = await f.read()
    return render_markdown(raw_content)


class GetChangelogService(BaseTemplateService):
    template_name = "changelog.html"

    async def get_context(self, *args, **kwargs) -> dict[str, Any]:
        return {
            "content": await _get_rendered_content(),
        }
