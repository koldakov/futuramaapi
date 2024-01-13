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
from app.repositories.models import (
    CharacterGenderFilter,
    CharacterSpeciesFilter,
    CharacterStatusFilter,
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


class BaseQueryException(Exception):
    ...


class CharacterQueryException(BaseQueryException):
    ...


class LimitViolation(CharacterQueryException):
    ...


class OffsetViolation(CharacterQueryException):
    ...


@strawberry.experimental.pydantic.type(model=CharacterSchema)
class Character:
    id: strawberry.auto
    name: strawberry.auto
    gender: strawberry.enum(CharacterGender)
    status: strawberry.enum(CharacterStatus)
    species: strawberry.enum(CharacterSpecies)
    created_at: strawberry.auto
    image: strawberry.auto


@strawberry.type
class Characters:
    limit: int
    offset: int
    total: int
    edges: List[Character]

    @classmethod
    def from_params(cls, characters, limit: int, offset: int, total: int, /):
        return cls(
            limit=limit,
            offset=offset,
            total=total,
            edges=[
                Character.from_pydantic(CharacterSchema.model_validate(character))
                for character in characters
            ],
        )


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
    async def characters(
        self,
        *,
        limit: int | None = 50,
        offset: int | None = 0,
        gender: strawberry.enum(CharacterGenderFilter) | None = None,
        status: strawberry.enum(CharacterStatusFilter) | None = None,
        species: strawberry.enum(CharacterSpeciesFilter) | None = None,
    ) -> Characters:
        # For some reason self does not work under strawberry decorator,
        # so class attrs can't be used. Please find another way.
        _min_l: int = 1
        _max_l: int = 50
        _min_offset: int = 0
        if not _min_l <= limit <= _max_l:
            raise LimitViolation(
                f"Limit can be more than {_min_l} and less than {_max_l}"
            ) from None

        async with get_async_session_ctx() as session:
            total: int = await CharacterModel.count(session)
            if not _min_offset <= offset <= total:
                raise LimitViolation(
                    f"Offset can't be less than {_min_offset} more than {total}"
                ) from None
            characters = await CharacterModel.filter(
                session,
                limit=limit,
                offset=offset,
                gender=gender,
                character_status=status,
                species=species,
            )
        return Characters.from_params(characters, limit, offset, total)

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
