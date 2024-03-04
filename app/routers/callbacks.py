from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.callbacks import (
    CallbackRequest,
    CallbackResponse,
    CharacterCallbackResponse,
    EpisodeCallbackResponse,
    SeasonCallbackResponse,
    process_characters_callback,
    process_episodes_callback,
    process_seasons_callback,
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
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> CallbackResponse:
    """Create a request to get a character by ID.

    Keep in mind for now there are no retries.

    * Send the character ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    return await process_characters_callback(character_id, character_request, session, background_tasks)


_episodes_callbacks_router = APIRouter()


@_episodes_callbacks_router.post(
    "{$callback_url}",
    status_code=status.HTTP_200_OK,
)
def episodes_callback(
    body: EpisodeCallbackResponse,
):
    """Request to the provided callback URL."""


@router.post(
    "/episodes/{episode_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CallbackResponse,
    name="episode",
    callbacks=_episodes_callbacks_router.routes,
)
async def create_episodes_callback_request(
    episode_id: int,
    episode_request: CallbackRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> CallbackResponse:
    """Create a request to get an episode by ID.

    Keep in mind for now there are no retries.

    * Send the episode ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    return await process_episodes_callback(episode_id, episode_request, session, background_tasks)


# Season related endpoints.
_seasons_callbacks_router = APIRouter()


@_seasons_callbacks_router.post(
    "{$callback_url}",
    status_code=status.HTTP_200_OK,
)
def seasons_callback(
    body: SeasonCallbackResponse,
):
    """Request to the provided callback URL."""


@router.post(
    "/seasons/{season_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CallbackResponse,
    name="season",
    callbacks=_seasons_callbacks_router.routes,
)
async def create_seasons_callback_request(
    season_id: int,
    season_request: CallbackRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> CallbackResponse:
    """Create a request to get a season by ID.

    Keep in mind for now there are no retries.

    * Send the season ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    return await process_seasons_callback(season_id, season_request, session, background_tasks)
