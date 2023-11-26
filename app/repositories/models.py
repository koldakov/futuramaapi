from enum import Enum
from typing import List
from uuid import uuid4

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    UUID as COLUMN_UUID,
    VARCHAR,
)
from sqlalchemy.dialects.postgresql import ENUM  # TODO: engine agnostic.
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.repositories.base import Base


class CharacterStatus(Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"
    UNKNOWN = "UNKNOWN"


class CharacterGender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNKNOWN = "UNKNOWN"


class CharacterSpecies(Enum):
    HUMAN = "HUMAN"
    ROBOT = "ROBOT"
    HEAD = "HEAD"
    ALIEN = "ALIEN"
    MUTANT = "MUTANT"
    MONSTER = "MONSTER"
    UNKNOWN = "UNKNOWN"


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


class EpisodeCharacterAssociation(Base):
    __tablename__ = "episode_character_association"

    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"), primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"), primary_key=True
    )

    character: Mapped["Character"] = relationship(back_populates="episode_associations")

    episode: Mapped["Episode"] = relationship(back_populates="character_associations")


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

    # Mappers
    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id"),
    )
    season: Mapped["Season"] = relationship(
        back_populates="episodes",
    )

    characters: Mapped[List["Character"]] = relationship(
        secondary="episode_character_association", back_populates="episodes"
    )

    character_associations: Mapped[List["EpisodeCharacterAssociation"]] = relationship(
        back_populates="episode"
    )


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

    # Mappers
    episodes: Mapped[List["Episode"]] = relationship(
        secondary="episode_character_association", back_populates="characters"
    )
    episode_associations: Mapped[List["EpisodeCharacterAssociation"]] = relationship(
        back_populates="character"
    )
