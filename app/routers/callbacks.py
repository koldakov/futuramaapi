from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.callbacks import (
    CallbackResponse,
    CallbackRequest,
    CharacterCallbackResponse,
    process_characters_callback,
)

router = APIRouter(prefix="/callbacks")

_characters_callbacks_router = APIRouter()


@_characters_callbacks_router.post(
    "{$callback_url}",
    status_code=status.HTTP_200_OK,
)
def character_callback(
    body: CharacterCallbackResponse,
):
    """Request to the provided callback URL."""


@router.post(
    "/characters/{character_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CallbackResponse,
    name="character",
    callbacks=_characters_callbacks_router.routes,
)
async def create_characters_callback_request(
    character_id: int,
    character_request: CallbackRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
) -> CallbackResponse:
    """Create a request to get a character by ID.

    Keep in mind for now there are no retries.

    * Send the character ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    return await process_characters_callback(
        character_id, character_request, session, background_tasks
    )
