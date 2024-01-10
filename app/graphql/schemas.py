from typing import List

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
)
from app.repositories.sessions import get_async_session_ctx
from app.services.base import EpisodeBase as EpisodeBaseSchema
from app.services.characters import Character as CharacterSchema
from app.services.episodes import (
    Episode as EpisodeSchema,
    SeasonEpisode as SeasonEpisodeSchema,
)
from app.services.seasons import (
    Season as SeasonSchema,
    EpisodeSeason as EpisodeSeasonSchema,
)


@strawberry.experimental.pydantic.type(model=CharacterSchema)
class Character:
    id: strawberry.auto
    name: strawberry.auto
    gender: strawberry.enum(CharacterGender)
    status: strawberry.enum(CharacterStatus)
    species: strawberry.enum(CharacterSpecies)
    created_at: strawberry.auto
    image: strawberry.auto


@strawberry.experimental.pydantic.type(model=SeasonEpisodeSchema, all_fields=True)
class SeasonEpisode:
    ...


@strawberry.experimental.pydantic.type(model=EpisodeBaseSchema, all_fields=True)
class EpisodeBase:
    ...


@strawberry.experimental.pydantic.type(model=EpisodeSchema)
class Episode(EpisodeBase):
    air_date: strawberry.auto
    duration: strawberry.auto
    created_at: strawberry.auto
    season: SeasonEpisode
    broadcast_code: str


@strawberry.experimental.pydantic.type(model=EpisodeSeasonSchema)
class EpisodeSeason(EpisodeBase):
    id: strawberry.auto
    name: strawberry.auto
    broadcast_number: strawberry.auto
    production_code: strawberry.auto


@strawberry.experimental.pydantic.type(model=SeasonSchema)
class Season:
    id: strawberry.auto
    episodes: List[EpisodeSeason]


@strawberry.type
class Query:
    @strawberry.field()
    async def character(self, character_id: int) -> Character | None:
        async with get_async_session_ctx() as session:
            try:
                character: CharacterModel = await CharacterModel.get(
                    session,
                    character_id,
                )
            except CharacterDoesNotExist:
                return None
        return Character.from_pydantic(CharacterSchema.model_validate(character))

    @strawberry.field()
    async def episode(self, episode_id: int) -> Episode | None:
        async with get_async_session_ctx() as session:
            try:
                episode: EpisodeModel = await EpisodeModel.get(
                    session,
                    episode_id,
                )
            except EpisodeDoesNotExist:
                return None
        return Episode.from_pydantic(EpisodeSchema.model_validate(episode))

    @strawberry.field()
    async def season(self, season_id: int) -> Season | None:
        async with get_async_session_ctx() as session:
            try:
                season: SeasonModel = await SeasonModel.get(session, season_id)
            except SeasonDoesNotExist:
                return None
        return Season.from_pydantic(SeasonSchema.model_validate(season))
