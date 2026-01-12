from typing import Annotated

from fastapi import APIRouter, Path, Request, status
from sse_starlette.sse import EventSourceResponse

from futuramaapi.repositories import INT32
from futuramaapi.routers.services.notifications.sse_character import (
    CharacterNotificationResponse,
    GetCharacterNotificationService,
)

router: APIRouter = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.get(
    "/sse/characters/{character_id}",
    response_class=EventSourceResponse,
    responses={
        status.HTTP_200_OK: {
            "model": CharacterNotificationResponse,
        }
    },
    status_code=status.HTTP_200_OK,
)
async def character_sse(
    character_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
    request: Request,
) -> EventSourceResponse:
    """Retrieve character path.

    Server-Sent Events (SSE) Endpoint for Character Paths:

    This SSE endpoint is designed for retrieving characters paths by passing the character ID.
    It facilitates real-time updates on character path.
    Exercise caution when using this endpoint to ensure responsible and accurate data retrieval.
    """
    service: GetCharacterNotificationService = GetCharacterNotificationService(
        pk=character_id,
    )
    return await service(request)
