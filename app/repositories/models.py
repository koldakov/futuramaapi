from enum import Enum
from typing import List, Type, override

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    VARCHAR,
    select,
)
from sqlalchemy.dialects.postgresql import ENUM  # TODO: engine agnostic.
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.sql.elements import BinaryExpression

from app.configs import settings
from app.repositories.base import Base, ModelDoesNotExist


def to_camel(
    val: str,
):
    return "".join(
        [
            word if idx == 0 else word.capitalize()
            for idx, word in enumerate(val.lower().split("_"))
        ]
    )


def generate_inverted_enum[T: Type[Enum]](
    name: str,
    proto_enum: T,
    /,
) -> T:
    return Enum(name, {f"NOT_{i.name}": f"!{i.value}" for i in [*proto_enum]})


def generate_filter_enum[T: Type[Enum]](
    name: str,
    enums: List[T],
) -> T:
    unpacked_enums: [List[T]] = [val for _e in enums for val in _e]
    return Enum(name, {e.name: to_camel(e.value) for e in unpacked_enums})


class CharacterStatus(Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"
    UNKNOWN = "UNKNOWN"


CharacterInvertedStatus = generate_inverted_enum(
    "CharacterInvertedStatus",
    CharacterStatus,
)


CharacterStatusFilter = generate_filter_enum(
    "CharacterStatusFilter",
    [
        CharacterStatus,
        CharacterInvertedStatus,
    ],
)


class CharacterGender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNKNOWN = "UNKNOWN"


CharacterInvertedGender = generate_inverted_enum(
    "CharacterInvertedGender",
    CharacterGender,
)


CharacterGenderFilter = generate_filter_enum(
    "CharacterGenderFilter",
    [
        CharacterGender,
        CharacterInvertedGender,
    ],
)


class CharacterSpecies(Enum):
    HUMAN = "HUMAN"
    ROBOT = "ROBOT"
    HEAD = "HEAD"
    ALIEN = "ALIEN"
    MUTANT = "MUTANT"
    MONSTER = "MONSTER"
    UNKNOWN = "UNKNOWN"


CharacterInvertedSpecies = generate_inverted_enum(
    "CharacterInvertedSpecies",
    CharacterSpecies,
)


CharacterSpeciesFilter = generate_filter_enum(
    "CharacterSpeciesFilter",
    [
        CharacterSpecies,
        CharacterInvertedSpecies,
    ],
)


class Season(Base):
    __tablename__ = "seasons"

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


class SeasonDoesNotExist(ModelDoesNotExist):
    """Season does not exist."""


class EpisodeCharacterAssociation(Base):
    __tablename__ = "episode_character_association"

    id = None
    created_at = None
    uuid = None
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

    name = Column(
        VARCHAR(
            length=128,
        ),
        nullable=True,
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


class EpisodeDoesNotExist(ModelDoesNotExist):
    """Episode does not exist."""


class CharacterOrderBy(Enum):
    ID = "id"
    NAME = "name"
    CREATED_AT = "createdAt"


class Character(Base):
    __tablename__ = "characters"
    order_by = CharacterOrderBy

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

    @classmethod
    @override
    def get_cond_list(cls, **kwargs) -> List[BinaryExpression]:
        gender: CharacterGenderFilter | None = kwargs.get("gender")
        character_status: CharacterStatusFilter | None = kwargs.get("character_status")
        species: CharacterSpeciesFilter | None = kwargs.get("species")
        query: str | None = kwargs.get("query")
        cond_list = []
        if gender is not None:
            cond_list.append(
                cls.filter_obj_to_cond(
                    gender,
                    CharacterGender,
                    Character.gender,
                )
            )
        if character_status is not None:
            cond_list.append(
                cls.filter_obj_to_cond(
                    character_status,
                    CharacterStatus,
                    Character.status,
                )
            )
        if species is not None:
            cond_list.append(
                cls.filter_obj_to_cond(
                    species,
                    CharacterSpecies,
                    Character.species,
                )
            )
        if query is not None:
            cond_list.append(Character.name.ilike(f"%{query.lower()}%"))
        return cond_list


class CharacterDoesNotExist(ModelDoesNotExist):
    """Character does not exist."""


class User(Base):
    __tablename__ = "users"

    name = Column(
        VARCHAR(
            length=64,
        ),
        nullable=False,
    )
    surname = Column(
        VARCHAR(
            length=64,
        ),
        nullable=False,
    )
    middle_name = Column(
        VARCHAR(
            length=64,
        ),
        nullable=True,
    )
    email = Column(
        VARCHAR(
            length=320,
        ),
        nullable=False,
        unique=True,
    )
    username = Column(
        VARCHAR(
            length=64,
        ),
        nullable=False,
        unique=True,
    )
    password = Column(
        VARCHAR(
            length=128,
        ),
        nullable=False,
    )
    is_confirmed = Column(
        Boolean,
        default=False,
    )
    is_subscribed = Column(
        Boolean,
        default=True,
    )


class UserDoesNotExist(ModelDoesNotExist):
    """User does not exist."""
