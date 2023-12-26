from asyncio import sleep
import json
from random import randint
from typing import Union

from fastapi import BackgroundTasks, HTTPException
from httpx import AsyncClient, Response
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.services.characters import Character
from app.services.episodes import Episode
from app.repositories.models import (
    CharacterDoesNotExist as CharacterDoesNotExistException,
    EpisodeDoesNotExist as EpisodeDoesNotExistException,
    SeasonDoesNotExist as SeasonDoesNotExistException,
    get_character,
    get_episode,
    get_season,
)
from app.services.seasons import Season

MIN_DELAY: int = 5
MAX_DELAY: int = 10


class CallbackRequest(BaseModel):
    callback_url: HttpUrl = Field(
        validation_alias="callbackUrl",
    )


class CallbackResponse(BaseModel):
    delay: int = Field(
        ge=MIN_DELAY,
        le=MAX_DELAY,
        description="Delay after which the callback will be sent.",
    )


class _ObjectDoesNotExist(BaseModel):
    id: int = Field(
        description="Requested object ID.",
    )
    detail: str = Field(
        examples=[
            "Not found",
        ],
    )


class CharacterDoesNotExist(_ObjectDoesNotExist):
    """Character does not exist response."""


class _ObjectType(BaseModel):
    type: str = Field(
        description="Requested Object type.",
    )


class CharacterCallbackResponse(_ObjectType):
    item: Union[Character, CharacterDoesNotExist]


async def _get_character_or_not_found_object(
    id_: int,
    session: AsyncSession,
    /,
) -> Union[Character, CharacterDoesNotExist]:
    character: Union[Character, CharacterDoesNotExist]
    try:
        character = await get_character(id_, session)
    except CharacterDoesNotExistException:
        character = CharacterDoesNotExist(
            id=id_,
            detail="Not found",
        )
    return character


async def _send_callback(url: HttpUrl, body: BaseModel, /):
    async with AsyncClient(http2=True) as client:
        callback_response: Response = await client.post(
            f"{url}",
            json=json.loads(body.model_dump_json(by_alias=True)),
        )
        callback_response.raise_for_status()


async def callback_characters_background_task(
    character_id: int,
    callback_request: CallbackRequest,
    response: CallbackResponse,
    session: AsyncSession,
    /,
):
    await sleep(response.delay)
    character: Union[
        Character,
        CharacterDoesNotExist,
    ] = await _get_character_or_not_found_object(character_id, session)
    body = CharacterCallbackResponse(
        type=Character.__name__,
        item=character,
    )
    await _send_callback(callback_request.callback_url, body)


async def process_characters_callback(
    character_id,
    callback_request: CallbackRequest,
    session: AsyncSession,
    background_tasks: BackgroundTasks,
    /,
) -> CallbackResponse:
    response: CallbackResponse = CallbackResponse(delay=randint(MIN_DELAY, MAX_DELAY))
    background_tasks.add_task(
        callback_characters_background_task,
        character_id,
        callback_request,
        response,
        session,
    )
    return response


class EpisodeDoesNotExist(_ObjectDoesNotExist):
    """Episode does not exist response."""


async def _get_episode_or_not_found_object(
    id_: int,
    session: AsyncSession,
    /,
) -> Union[Episode, EpisodeDoesNotExist]:
    episode: Union[Episode, EpisodeDoesNotExist]
    try:
        episode = await get_episode(id_, session)
    except EpisodeDoesNotExistException:
        episode = EpisodeDoesNotExist(
            id=id_,
            detail="Not found",
        )
    return episode


class EpisodeCallbackResponse(_ObjectType):
    item: Union[Episode, EpisodeDoesNotExist]


async def callback_episodes_background_task(
    episode_id: int,
    callback_request: CallbackRequest,
    response: CallbackResponse,
    session: AsyncSession,
    /,
):
    await sleep(response.delay)
    episode: Union[
        Episode,
        EpisodeDoesNotExist,
    ] = await _get_episode_or_not_found_object(episode_id, session)
    body = EpisodeCallbackResponse(
        type=Episode.__name__,
        item=episode,
    )
    await _send_callback(callback_request.callback_url, body)


async def process_episodes_callback(
    episode_id,
    episode_request,
    session,
    background_tasks,
) -> CallbackResponse:
    response: CallbackResponse = CallbackResponse(delay=randint(MIN_DELAY, MAX_DELAY))
    background_tasks.add_task(
        callback_episodes_background_task,
        episode_id,
        episode_request,
        response,
        session,
    )
    return response


# Season related part.
class SeasonDoesNotExist(_ObjectDoesNotExist):
    """Season does not exist response."""


async def _get_season_or_not_found_object(
    id_: int,
    session: AsyncSession,
    /,
) -> Union[Season, SeasonDoesNotExist]:
    season: Union[Season, SeasonDoesNotExist]
    try:
        season = await get_season(id_, session)
    except SeasonDoesNotExistException:
        season = SeasonDoesNotExist(
            id=id_,
            detail="Not found",
        )
    return season


class SeasonCallbackResponse(_ObjectType):
    item: Union[Season, SeasonDoesNotExist]


async def callback_seasons_background_task(
    season_id: int,
    callback_request: CallbackRequest,
    response: CallbackResponse,
    session: AsyncSession,
    /,
):
    await sleep(response.delay)
    season: Union[
        Season,
        SeasonDoesNotExist,
    ] = await _get_season_or_not_found_object(season_id, session)
    body = SeasonCallbackResponse(
        type=Season.__name__,
        item=season,
    )
    await _send_callback(callback_request.callback_url, body)


async def process_seasons_callback(
    season_id,
    season_request,
    session,
    background_tasks,
) -> CallbackResponse:
    response: CallbackResponse = CallbackResponse(delay=randint(MIN_DELAY, MAX_DELAY))
    background_tasks.add_task(
        callback_seasons_background_task,
        season_id,
        season_request,
        response,
        session,
    )
    return response
