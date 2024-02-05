from fastapi import Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.models import Character as CharacterModel, User as UserModel
from app.templates import templates


async def process_get_root(
    request: Request,
    session: AsyncSession,
    /,
) -> Response:
    characters = await CharacterModel.filter(session, limit=6)
    user_count = await UserModel.count(session)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "characters": characters,
            "user_count": user_count,
        },
    )


async def process_about(
    request: Request,
    /,
) -> Response:
    return templates.TemplateResponse(
        request,
        "about.html",
    )
