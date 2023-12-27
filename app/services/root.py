from fastapi import Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.models import Character as CharacterModel
from app.templates import templates


async def process_get_root(
    request: Request,
    session: AsyncSession,
    /,
) -> Response:
    cursor: Result = await session.execute(
        select(CharacterModel).order_by("id").limit(6)
    )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "characters": cursor.scalars().all(),
        },
    )


async def process_about(
    request: Request,
    /,
) -> Response:
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
        },
    )
