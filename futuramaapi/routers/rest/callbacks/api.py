from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Path, status

from futuramaapi.repositories import INT32
from futuramaapi.routers.services.callbacks import (
    CallbackRequest,
    CallbackResponse,
)
from futuramaapi.routers.services.callbacks.get_character import (
    GetCharacterCallbackService,
)
from futuramaapi.routers.services.callbacks.get_episode import (
    GetEpisodeCallbackService,
)
from futuramaapi.routers.services.callbacks.get_season import (
    GetSeasonCallbackService,
)
from futuramaapi.workers.services.callbacks import (
    GetCharacterCallbackResponse,
    GetEpisodeCallbackResponse,
    GetSeasonCallbackResponse,
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
    body: GetCharacterCallbackResponse,
):
    """Request to the provided callback URL."""


@router.post(
    "/characters/{character_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CallbackResponse,
    name="character_callback",
    callbacks=_characters_callbacks_router.routes,
)
async def create_characters_callback_request(
    character_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
    request: CallbackRequest,
    background_tasks: BackgroundTasks,
) -> CallbackResponse:
    """Create a request to get a character by ID.

    Keep in mind for now there are no retries.

    * Send the character ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    service: GetCharacterCallbackService = GetCharacterCallbackService(
        request_data=request,
        id=character_id,
    )
    return await service(background_tasks)


_episodes_callbacks_router = APIRouter()


@_episodes_callbacks_router.post(
    "{$callback_url}",
    status_code=status.HTTP_200_OK,
)
def episodes_callback(
    body: GetEpisodeCallbackResponse,
):
    """Request to the provided callback URL."""


@router.post(
    "/episodes/{episode_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CallbackResponse,
    name="episode_callback",
    callbacks=_episodes_callbacks_router.routes,
)
async def create_episodes_callback_request(
    episode_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
    request: CallbackRequest,
    background_tasks: BackgroundTasks,
) -> CallbackResponse:
    """Create a request to get an episode by ID.

    Keep in mind for now there are no retries.

    * Send the episode ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    service: GetEpisodeCallbackService = GetEpisodeCallbackService(
        request_data=request,
        id=episode_id,
    )
    return await service(background_tasks)


# Season related endpoints.
_seasons_callbacks_router = APIRouter()


@_seasons_callbacks_router.post(
    "{$callback_url}",
    status_code=status.HTTP_200_OK,
)
def seasons_callback(
    body: GetSeasonCallbackResponse,
):
    """Request to the provided callback URL."""


@router.post(
    "/seasons/{season_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CallbackResponse,
    name="season_callback",
    callbacks=_seasons_callbacks_router.routes,
)
async def create_seasons_callback_request(
    season_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
    request: CallbackRequest,
    background_tasks: BackgroundTasks,
) -> CallbackResponse:
    """Create a request to get a season by ID.

    Keep in mind for now there are no retries.

    * Send the season ID you want to request via callback.
    * Receive a delay after which the callback will be sent.
    * Receive a notification back to the API, as a callback.
    """
    service: GetSeasonCallbackService = GetSeasonCallbackService(
        request_data=request,
        id=season_id,
    )
    return await service(background_tasks)
