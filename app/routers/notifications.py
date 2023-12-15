from fastapi import APIRouter, Depends, Request, status
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.notifications import CharacterMove, process_sse
from app.templates import gnu_translations

router = APIRouter(
    prefix="/notifications",
)


@router.get(
    "/sse/characters/{character_id}",
    response_class=EventSourceResponse,
    responses={
        status.HTTP_200_OK: {
            "model": CharacterMove,
        }
    },
    status_code=status.HTTP_200_OK,
    description=gnu_translations.gettext("FB00010"),
)
async def sse(
    character_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> EventSourceResponse:
    return await process_sse(character_id, request, session)
