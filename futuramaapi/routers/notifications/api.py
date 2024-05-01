from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sse_starlette.sse import EventSourceResponse

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError

from .schemas import CharacterNotification

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.get(
    "/sse/characters/{character_id}",
    response_class=EventSourceResponse,
    responses={
        status.HTTP_200_OK: {
            "model": CharacterNotification,
        }
    },
    status_code=status.HTTP_200_OK,
)
async def character_sse(
    character_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> EventSourceResponse:
    """Retrieve character path.

    Server-Sent Events (SSE) Endpoint for Character Paths:

    This SSE endpoint is designed for retrieving characters paths by passing the character ID.
    It facilitates real-time updates on character path.
    Exercise caution when using this endpoint to ensure responsible and accurate data retrieval.
    """
    try:
        return await CharacterNotification.from_request(character_id, request, session)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Character with id={character_id} not found",
        ) from None
