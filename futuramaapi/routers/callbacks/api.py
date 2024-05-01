from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.callbacks.schemas import Character
from futuramaapi.routers.episodes.schemas import Episode
from futuramaapi.routers.seasons.schemas import Season

from .schemas import (
    CallbackObjectResponse,
    CallbackRequest,
    CallbackResponse,
)

router = APIRouter(
    prefix="/callbacks",
    tags=["callbacks"],
)

_characters_callbacks_router = APIRouter()


@_characters_callbacks_router.post(
    "{$callback_url}",
    status_code=status.HTTP_200_OK,
)
def character_callback(
    body: CallbackObjectResponse,
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
    request: CallbackRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> CallbackResponse:
    """Create a request to get a character by ID.

    Keep in mind for now there are no retries.

    * Send the character ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    return await CallbackResponse.process(session, Character, request, character_id, background_tasks)


_episodes_callbacks_router = APIRouter()


@_episodes_callbacks_router.post(
    "{$callback_url}",
    status_code=status.HTTP_200_OK,
)
def episodes_callback(
    body: CallbackObjectResponse,
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
    request: CallbackRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> CallbackResponse:
    """Create a request to get an episode by ID.

    Keep in mind for now there are no retries.

    * Send the episode ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    return await CallbackResponse.process(session, Episode, request, episode_id, background_tasks)


# Season related endpoints.
_seasons_callbacks_router = APIRouter()


@_seasons_callbacks_router.post(
    "{$callback_url}",
    status_code=status.HTTP_200_OK,
)
def seasons_callback(
    body: CallbackObjectResponse,
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
    request: CallbackRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> CallbackResponse:
    """Create a request to get a season by ID.

    Keep in mind for now there are no retries.

    * Send the season ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    return await CallbackResponse.process(session, Season, request, season_id, background_tasks)
