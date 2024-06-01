from enum import Enum

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
)
from sqlalchemy.dialects.postgresql import ENUM  # TODO: engine agnostic.
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql.elements import BinaryExpression

from futuramaapi.core import settings
from futuramaapi.repositories.base import Base


class SeasonModel(Base):
    __tablename__ = "seasons"

    # Mappers
    episodes: Mapped[list["EpisodeModel"]] = relationship(
        back_populates="season",
    )

    @staticmethod
    def get_select_in_load() -> list[Load]:
        return [selectinload(SeasonModel.episodes)]


class EpisodeCharacterAssociationModel(Base):
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


class EpisodeModel(Base):
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
    season: Mapped["SeasonModel"] = relationship(
        back_populates="episodes",
    )

    characters: Mapped[list["CharacterModel"]] = relationship(
        secondary="episode_character_association",
        back_populates="episodes",
    )

    @staticmethod
    def get_select_in_load() -> list[Load]:
        return [selectinload(EpisodeModel.season)]


class CharacterModel(Base):
    __tablename__ = "characters"

    class CharacterSpecies(Enum):
        HUMAN = "HUMAN"
        ROBOT = "ROBOT"
        HEAD = "HEAD"
        ALIEN = "ALIEN"
        MUTANT = "MUTANT"
        MONSTER = "MONSTER"
        UNKNOWN = "UNKNOWN"

    class CharacterStatus(Enum):
        ALIVE = "ALIVE"
        DEAD = "DEAD"
        UNKNOWN = "UNKNOWN"

    class CharacterGender(Enum):
        MALE = "MALE"
        FEMALE = "FEMALE"
        UNKNOWN = "UNKNOWN"

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
    episodes: Mapped[list["EpisodeModel"]] = relationship(
        secondary="episode_character_association",
        back_populates="characters",
    )

    @classmethod
    def get_cond_list(cls, **kwargs) -> list[BinaryExpression]:
        gender: str | None = kwargs.get("gender")
        status: str | None = kwargs.get("status")
        species: str | None = kwargs.get("species")
        query: str | None = kwargs.get("query")

        cond_list = []
        if gender is not None:
            gender = gender.upper()
            cond_list.append(cls.get_binary_cond(cls.gender, gender))
        if status is not None:
            status = status.upper()
            cond_list.append(cls.get_binary_cond(cls.status, status))
        if species is not None:
            species = species.upper()
            cond_list.append(cls.get_binary_cond(cls.species, species))

        if query is not None:
            cond_list.append(cls.name.ilike(f"%{query.lower()}%"))
        return cond_list


class UserModel(Base):
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
