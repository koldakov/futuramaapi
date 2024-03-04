from typing import Any

import strawberry

from app.repositories.models import (
    Character as CharacterModel,
)
from app.repositories.models import (
    CharacterDoesNotExist,
    CharacterGender,
    CharacterGenderFilter,
    CharacterSpecies,
    CharacterSpeciesFilter,
    CharacterStatus,
    CharacterStatusFilter,
    EpisodeDoesNotExist,
    SeasonDoesNotExist,
)
from app.repositories.models import (
    Episode as EpisodeModel,
)
from app.repositories.models import (
    Season as SeasonModel,
)
from app.repositories.sessions import get_async_session_ctx
from app.services.base import EpisodeBase as EpisodeBaseSchema
from app.services.characters import Character as CharacterSchema
from app.services.episodes import (
    Episode as EpisodeSchema,
)
from app.services.episodes import (
    SeasonEpisode as SeasonEpisodeSchema,
)
from app.services.seasons import (
    EpisodeSeason as EpisodeSeasonSchema,
)
from app.services.seasons import (
    Season as SeasonSchema,
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
    id: strawberry.auto  # noqa: A003
    name: strawberry.auto
    gender: strawberry.enum(CharacterGender)  # type: ignore
    status: strawberry.enum(CharacterStatus)  # type: ignore
    species: strawberry.enum(CharacterSpecies)  # type: ignore
    created_at: strawberry.auto
    image: strawberry.auto


@strawberry.type
class PageBase:
    limit: int
    offset: int
    total: int
    edges: list[Any]

    @staticmethod
    def get_schema_class():
        raise NotImplementedError()

    @staticmethod
    def get_edge_class():
        raise NotImplementedError()

    @classmethod
    def from_params(cls, edges, limit: int, offset: int, total: int, /):
        schema_class = cls.get_schema_class()
        edge_class = cls.get_edge_class()
        return cls(
            limit=limit,  # type: ignore
            offset=offset,  # type: ignore
            total=total,  # type: ignore
            edges=[edge_class.from_pydantic(schema_class.model_validate(edge)) for edge in edges],  # type: ignore
        )


@strawberry.type
class Characters(PageBase):
    edges: list[Character]

    @staticmethod
    def get_schema_class():
        return CharacterSchema

    @staticmethod
    def get_edge_class():
        return Character


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
    id: strawberry.auto  # noqa: A003
    name: strawberry.auto
    broadcast_number: strawberry.auto
    production_code: strawberry.auto


@strawberry.type
class Episodes(PageBase):
    edges: list[Episode]

    @staticmethod
    def get_schema_class():
        return EpisodeSchema

    @staticmethod
    def get_edge_class():
        return Episode


@strawberry.experimental.pydantic.type(model=SeasonSchema)
class Season:
    id: strawberry.auto  # noqa: A003
    episodes: list[EpisodeSeason]


def validate_limit(limit: int, min_: int, max_: int, /) -> None:
    if not min_ <= limit <= max_:
        raise LimitViolation(f"Limit can be more than {min_} and less than {max_}") from None


@strawberry.type
class Seasons(PageBase):
    edges: list[Season]

    @staticmethod
    def get_schema_class():
        return SeasonSchema

    @staticmethod
    def get_edge_class():
        return Season


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
        return Character.from_pydantic(CharacterSchema.model_validate(character))  # type: ignore

    @strawberry.field()
    async def characters(  # noqa: PLR0913
        self,
        *,
        limit: int | None = 50,
        offset: int | None = 0,
        gender: strawberry.enum(CharacterGenderFilter) | None = None,  # type: ignore
        status: strawberry.enum(CharacterStatusFilter) | None = None,  # type: ignore
        species: strawberry.enum(CharacterSpeciesFilter) | None = None,  # type: ignore
    ) -> Characters:
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        # For some reason self does not work under strawberry decorator,
        # so class attrs can't be used. Please find another way.
        _min_l: int = 1
        _max_l: int = 50
        _min_offset: int = 0
        validate_limit(limit, _min_l, _max_l)

        async with get_async_session_ctx() as session:
            total: int = await CharacterModel.count(session)
            validate_limit(offset, _min_offset, total)
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
        return Episode.from_pydantic(EpisodeSchema.model_validate(episode))  # type: ignore

    @strawberry.field()
    async def episodes(
        self,
        *,
        limit: int | None = 50,
        offset: int | None = 0,
    ) -> Episodes:
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        validate_limit(limit, 1, 50)
        async with get_async_session_ctx() as session:
            total: int = await CharacterModel.count(session)
            validate_limit(offset, 0, total)
            episodes = await EpisodeModel.filter(
                session,
                limit=limit,
                select_in_load=EpisodeModel.season,
                offset=offset,
            )
        return Episodes.from_params(episodes, limit, offset, total)

    @strawberry.field()
    async def season(self, season_id: int) -> Season | None:
        async with get_async_session_ctx() as session:
            try:
                season: SeasonModel = await SeasonModel.get(session, season_id)
            except SeasonDoesNotExist:
                return None
        return Season.from_pydantic(SeasonSchema.model_validate(season))  # type: ignore

    @strawberry.field()
    async def seasons(
        self,
        *,
        limit: int | None = 50,
        offset: int | None = 0,
    ) -> Seasons:
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        validate_limit(limit, 1, 50)
        async with get_async_session_ctx() as session:
            total: int = await SeasonModel.count(session)
            validate_limit(offset, 0, total)
            seasons = await SeasonModel.filter(
                session,
                limit=limit,
                select_in_load=SeasonModel.episodes,
                offset=offset,
            )
        return Seasons.from_params(seasons, limit, offset, total)
