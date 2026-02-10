from datetime import date, datetime
from enum import StrEnum
from typing import Any, ClassVar

import strawberry
from strawberry.types import Info

from futuramaapi.db import Base, FilterStatementKwargs
from futuramaapi.db.models import CharacterModel, EpisodeModel, SeasonModel

from .mixins import StrawberryDatabaseMixin
from .validators import LimitsRule


@strawberry.type
class PageBase(StrawberryDatabaseMixin):
    limit: int
    offset: int
    total: int
    edges: list[Any]


@strawberry.type
class Character(StrawberryDatabaseMixin):
    model: ClassVar[type[Base]] = CharacterModel

    id: int
    name: str
    status: strawberry.enum(CharacterModel.CharacterStatus)  # type: ignore[valid-type]
    gender: strawberry.enum(CharacterModel.CharacterGender)  # type: ignore[valid-type]
    species: strawberry.enum(CharacterModel.CharacterSpecies)  # type: ignore[valid-type]
    image: str | None


@strawberry.type
class Characters(PageBase, StrawberryDatabaseMixin):
    model: ClassVar[type[Base]] = CharacterModel

    edges: list[Character]


@strawberry.type
class Episode(StrawberryDatabaseMixin):
    model: ClassVar[type[Base]] = EpisodeModel

    @strawberry.type
    class SeasonEpisode(StrawberryDatabaseMixin):
        model: ClassVar[type[Base]] = SeasonModel

        id: int

    id: int
    air_date: date | None
    duration: int | None
    created_at: datetime
    season: SeasonEpisode


@strawberry.type
class Episodes(PageBase, StrawberryDatabaseMixin):
    model: ClassVar[type[Base]] = EpisodeModel

    edges: list[Episode]


@strawberry.type
class Season(StrawberryDatabaseMixin):
    model: ClassVar[type[Base]] = SeasonModel

    @strawberry.type
    class EpisodeSeason(StrawberryDatabaseMixin):
        model: ClassVar[type[Base]] = EpisodeModel

        id: int
        air_date: date | None
        duration: int | None
        created_at: datetime

    id: int
    episodes: list[EpisodeSeason]


@strawberry.type
class Seasons(PageBase, StrawberryDatabaseMixin):
    model: ClassVar[type[Base]] = SeasonModel

    edges: list[Season]


@strawberry.type
class Query:
    @strawberry.enum
    class GenderFilter(StrEnum):
        male = "male"
        not_male = "!male"
        female = "female"
        not_femail = "!female"
        unknown = "unknown"
        not_unknown = "!unknown"

    @strawberry.enum
    class StatusFilter(StrEnum):
        alive = "alive"
        not_alive = "!alive"
        dead = "dead"
        not_dead = "!dead"
        unknown = "unknown"
        not_unknown = "!unknown"

    @strawberry.enum
    class SpeciesFilter(StrEnum):
        human = "human"
        not_human = "!human"
        robot = "robot"
        not_robot = "!robot"
        head = "head"
        not_head = "!head"
        alien = "alien"
        not_alien = "!alien"
        mutant = "mutant"
        not_mutant = "!mutant"
        monster = "monster"
        not_monster = "!monster"
        unknown = "unknown"
        not_unknown = "!unknown"

    @strawberry.field()
    async def character(
        self,
        info: Info,
        character_id: int,
    ) -> Character | None:
        return await Character.get(info.context.session, character_id)

    @strawberry.field(
        extensions=[
            LimitsRule(),
        ],
    )
    async def characters(  # noqa: PLR0913
        self,
        info: Info,
        limit: int | None = 50,
        offset: int | None = 0,
        gender: GenderFilter | None = None,
        status: StatusFilter | None = None,
        species: SpeciesFilter | None = None,
    ) -> Characters:
        kwargs: FilterStatementKwargs = FilterStatementKwargs(
            offset=offset,
            limit=limit,
            extra={
                "gender": gender,
                "species": species,
                "status": status,
            },
        )

        return await Characters.paginate(info.context.session, kwargs)

    @strawberry.field()
    async def episode(
        self,
        info: Info,
        episode_id: int,
    ) -> Episode | None:
        return await Episode.get(info.context.session, episode_id)

    @strawberry.field(
        extensions=[
            LimitsRule(),
        ],
    )
    async def episodes(
        self,
        info: Info,
        *,
        limit: int | None = 50,
        offset: int | None = 0,
    ) -> Episodes:
        kwargs: FilterStatementKwargs = FilterStatementKwargs(
            offset=offset,
            limit=limit,
        )

        return await Episodes.paginate(info.context.session, kwargs)

    @strawberry.field()
    async def season(
        self,
        info: Info,
        season_id: int,
    ) -> Season | None:
        return await Season.get(info.context.session, season_id)

    @strawberry.field(
        extensions=[
            LimitsRule(),
        ],
    )
    async def seasons(
        self,
        info: Info,
        *,
        limit: int | None = 50,
        offset: int | None = 0,
    ) -> Seasons:
        kwargs: FilterStatementKwargs = FilterStatementKwargs(
            offset=offset,
            limit=limit,
        )

        return await Seasons.paginate(info.context.session, kwargs)
