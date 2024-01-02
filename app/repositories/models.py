from enum import Enum
from typing import List, Optional, Type, Union, override
from uuid import uuid4

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    UUID as COLUMN_UUID,
    VARCHAR,
    select,
)
from sqlalchemy.dialects.postgresql import ENUM  # TODO: engine agnostic.
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.sql import func

from app.configs import settings
from app.repositories.base import Base


def to_camel(
    val: str,
):
    return "".join(
        [
            word if idx == 0 else word.capitalize()
            for idx, word in enumerate(val.lower().split("_"))
        ]
    )


class CharacterStatus(Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"
    UNKNOWN = "UNKNOWN"


class CharacterInvertedStatus(Enum):
    NOT_ALIVE = "!ALIVE"
    NOT_DEAD = "!DEAD"
    NOT_UNKNOWN = "!UNKNOWN"


CharacterStatusFilter = Enum(
    "CharacterStatusFilter",
    {
        i.name: to_camel(i.value)
        for i in [
            *CharacterStatus,
            *CharacterInvertedStatus,
        ]
    },
)


class CharacterGender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNKNOWN = "UNKNOWN"


class CharacterInvertedGender(Enum):
    NOT_MALE = "!MALE"
    NOT_FEMALE = "!FEMALE"
    NOT_UNKNOWN = "!UNKNOWN"


CharacterGenderFilter = Enum(
    "CharacterGenderFilter",
    {
        i.name: to_camel(i.value)
        for i in [
            *CharacterGender,
            *CharacterInvertedGender,
        ]
    },
)


class CharacterSpecies(Enum):
    HUMAN = "HUMAN"
    ROBOT = "ROBOT"
    HEAD = "HEAD"
    ALIEN = "ALIEN"
    MUTANT = "MUTANT"
    MONSTER = "MONSTER"
    UNKNOWN = "UNKNOWN"


class CharacterInvertedSpecies(Enum):
    NOT_HUMAN = "!HUMAN"
    NOT_ROBOT = "!ROBOT"
    NOT_HEAD = "!HEAD"
    NOT_ALIEN = "!ALIEN"
    NOT_MUTANT = "!MUTANT"
    NOT_MONSTER = "!MONSTER"
    NOT_UNKNOWN = "!UNKNOWN"


CharacterSpeciesFilter = Enum(
    "CharacterSpeciesFilter",
    {
        i.name: to_camel(i.value)
        for i in [
            *CharacterSpecies,
            *CharacterInvertedSpecies,
        ]
    },
)


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    created_at = Column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )
    uuid = Column(
        COLUMN_UUID(
            as_uuid=True,
        ),
        primary_key=False,
        unique=True,
        nullable=False,
        default=uuid4,
    )

    # Mappers
    episodes: Mapped[List["Episode"]] = relationship(
        back_populates="season",
    )

    @classmethod
    @override
    async def get(
        cls,
        session: AsyncSession,
        id_: int,
        /,
    ) -> "Season":
        cursor: Result = await session.execute(
            select(Season)
            .where(Season.id == id_)
            .options(selectinload(Season.episodes))
        )
        try:
            return cursor.scalars().one()
        except NoResultFound as err:
            raise SeasonDoesNotExist() from err


class SeasonDoesNotExist(Exception):
    """Season does not exist."""


class EpisodeCharacterAssociation(Base):
    __tablename__ = "episode_character_association"

    episode_id: Mapped[int] = mapped_column(
        ForeignKey("episodes.id"),
        primary_key=True,
    )
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"),
        primary_key=True,
    )


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True)

    name = Column(
        VARCHAR(
            length=128,
        ),
        nullable=True,
    )
    created_at = Column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )
    uuid = Column(
        COLUMN_UUID(
            as_uuid=True,
        ),
        primary_key=False,
        unique=True,
        nullable=False,
        default=uuid4,
    )
    air_date = Column(
        Date(),
        nullable=True,
    )
    duration = Column(
        Integer,
        nullable=True,
    )
    production_code = Column(
        VARCHAR(
            length=8,
        ),
        nullable=True,
    )
    broadcast_number = Column(
        SmallInteger,
        nullable=True,
    )

    # Mappers
    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id"),
    )
    season: Mapped["Season"] = relationship(
        back_populates="episodes",
    )

    characters: Mapped[List["Character"]] = relationship(
        secondary="episode_character_association",
        back_populates="episodes",
    )

    @classmethod
    @override
    async def get(
        cls,
        session: AsyncSession,
        id_: int,
        /,
    ) -> "Episode":
        cursor: Result = await session.execute(
            select(Episode)
            .where(Episode.id == id_)
            .options(selectinload(Episode.season))
        )
        try:
            return cursor.scalars().one()
        except NoResultFound as err:
            raise EpisodeDoesNotExist() from err


class EpisodeDoesNotExist(Exception):
    """Episode does not exist."""


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)

    name = Column(
        VARCHAR(
            length=128,
        ),
        nullable=False,
    )
    status = Column(
        ENUM(
            CharacterStatus,
        ),
        nullable=False,
    )
    created_at = Column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )
    gender = Column(
        ENUM(
            CharacterGender,
        ),
        nullable=False,
    )
    species = Column(
        ENUM(
            CharacterSpecies,
        ),
        nullable=False,
    )
    uuid = Column(
        COLUMN_UUID(
            as_uuid=True,
        ),
        primary_key=False,
        unique=True,
        nullable=False,
        default=uuid4,
    )
    image = Column(
        ImageType(
            storage=FileSystemStorage(path=settings.project_root / settings.static),
        ),
    )

    # Mappers
    episodes: Mapped[List["Episode"]] = relationship(
        secondary="episode_character_association",
        back_populates="characters",
    )

    @classmethod
    @override
    async def get(
        cls,
        session: AsyncSession,
        id_: int,
        /,
    ) -> "Character":
        cursor: Result = await session.execute(
            select(Character).where(Character.id == id_)
        )
        try:
            return cursor.scalars().one()
        except NoResultFound as err:
            raise CharacterDoesNotExist() from err


class CharacterDoesNotExist(Exception):
    """Character does not exist."""


def _get_cond(
    filter_obj: Union[
        CharacterGenderFilter,
        CharacterSpeciesFilter,
        CharacterStatusFilter,
    ],
    orig_enum: Union[
        Type[CharacterGender],
        Type[CharacterStatus],
        Type[CharacterSpecies],
    ],
    model_field: Column[Union[str, Enum]],
    /,
):
    if filter_obj.name.startswith("NOT_"):
        return model_field != orig_enum[filter_obj.name.split("NOT_", 1)[1]]
    else:
        return model_field == orig_enum[filter_obj.name]


def get_characters_cond(
    *,
    gender: Optional[CharacterGenderFilter] = None,
    character_status: Optional[CharacterStatusFilter] = None,
    species: Optional[CharacterSpeciesFilter] = None,
    query: Optional[str] = None,
) -> List:
    cond = []
    if gender is not None:
        cond.append(_get_cond(gender, CharacterGender, Character.gender))
    if character_status is not None:
        cond.append(_get_cond(character_status, CharacterStatus, Character.status))
    if species is not None:
        cond.append(_get_cond(species, CharacterSpecies, Character.species))
    if query is not None:
        cond.append(Character.name.ilike(f"%{query.lower()}%"))
    return cond
