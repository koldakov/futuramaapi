from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi_storages.base import StorageImage
import strawberry

from app.repositories.models import (
    Character as CharacterModel,
    CharacterDoesNotExist,
    CharacterGender,
    CharacterSpecies,
    CharacterStatus,
    Episode as EpisodeModel,
    EpisodeDoesNotExist,
    Season as SeasonModel,
    SeasonDoesNotExist,
    get_character,
    get_episode,
    get_season,
)
from app.repositories.sessions import get_async_session_ctx
from app.services.characters import build_url


_Status = strawberry.enum(CharacterStatus)
_Gender = strawberry.enum(CharacterGender)
_Species = strawberry.enum(CharacterSpecies)


@strawberry.type
class CharacterResponse:
    id: int
    name: str
    status: _Status
    created_at: datetime
    gender: _Gender
    species: _Species
    uuid: UUID
    image: Optional[str]


@strawberry.type
class SeasonBase:
    id: int
    created_at: datetime
    uuid: UUID


@strawberry.type
class EpisodeSeason(SeasonBase):
    """Season model for episode response.

    We don't need to return episodes in season on episode request.
    """


@strawberry.type
class EpisodeBase:
    id: int
    name: str
    created_at: datetime
    uuid: UUID
    air_date: Optional[date]
    duration: Optional[int]
    production_code: str
    broadcast_number: int


@strawberry.type
class EpisodeResponse(EpisodeBase):
    season: EpisodeSeason


@strawberry.type
class SeasonEpisode(EpisodeBase):
    """Episode model for season response.

    We don't need to return season in episode on season request.
    """


@strawberry.type
class SeasonResponse(SeasonBase):
    episodes: List[SeasonEpisode]


@strawberry.type
class Query:
    @strawberry.field
    async def character(self, character_id: int) -> Optional[CharacterResponse]:
        async with get_async_session_ctx() as session:
            try:
                character: CharacterModel = await CharacterModel.get(
                    session,
                    character_id,
                )
            except CharacterDoesNotExist:
                return None
        data: dict = character.to_dict()
        image: StorageImage = data.pop("image")
        return CharacterResponse(
            **data,
            image=build_url(path=image._name),  # noqa
        )

    @strawberry.field
    async def episode(self, episode_id: int) -> Optional[EpisodeResponse]:
        async with get_async_session_ctx() as session:
            try:
                episode: EpisodeModel = await EpisodeModel.get(session, episode_id)
            except EpisodeDoesNotExist:
                return None
        return EpisodeResponse(**episode.to_dict(exclude=["season_id"]))

    @strawberry.field
    async def season(self, season_id: int) -> Optional[SeasonResponse]:
        async with get_async_session_ctx() as session:
            try:
                season: SeasonModel = await SeasonModel.get(session, season_id)
            except SeasonDoesNotExist:
                return None
        return SeasonResponse(**season.to_dict())
