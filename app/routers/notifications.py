from fastapi import APIRouter, Depends, Request, status
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.notifications import CharacterMove, process_character_sse

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
)
async def character_sse(
    character_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> EventSourceResponse:
    """Retrieve character path.

    Server-Sent Events (SSE) Endpoint for Character Paths:

    This SSE endpoint is designed for retrieving characters paths by passing the character ID.
    It facilitates real-time updates on character path.
    Exercise caution when using this endpoint to ensure responsible and accurate data retrieval.
    """
    return await process_character_sse(character_id, request, session)
