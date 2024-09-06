from datetime import UTC, datetime, timedelta
from enum import Enum
from functools import lru_cache, partial

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import (
    BIGINT,
    TEXT,
    VARCHAR,
    BigInteger,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    Update,
    update,
)
from sqlalchemy.dialects.postgresql import ENUM  # TODO: engine agnostic.
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql.elements import BinaryExpression

from futuramaapi.core import settings
from futuramaapi.helpers.hashers import hasher
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
    links: Mapped[list["LinkModel"]] = relationship(
        back_populates="user",
    )

    active_sessions: Mapped[list["AuthSessionModel"]] = relationship(
        back_populates="user",
    )

    @staticmethod
    def get_select_in_load() -> list[Load]:
        return [
            selectinload(UserModel.links),
            selectinload(UserModel.active_sessions),
        ]

    @classmethod
    def get_cond_list(cls, **kwargs) -> list[BinaryExpression]:
        query: str | None = kwargs.get("query")

        cond_list = []
        if query is not None:
            cond_list.append(cls.username.ilike(f"%{query.lower()}%"))
        return cond_list


def _generate_shortened(length: int, /) -> str:
    shortened: str
    while True:
        shortened = hasher.get_random_string(length)
        if LinkModel.is_shortened_allowed(shortened):
            return shortened


@lru_cache
def _get_forbidden_shortened() -> set[str]:
    from futuramaapi.apps.app import futurama_api

    return futurama_api.urls


class LinkModel(Base):
    __tablename__ = "links"

    @staticmethod
    def is_shortened_allowed(shortened: str, /) -> bool:
        return True

    shortened_length: int = 7

    url = Column(
        VARCHAR(
            length=4096,
        ),
        nullable=False,
    )
    shortened = Column(
        VARCHAR(
            length=128,
        ),
        nullable=False,
        unique=True,
        default=partial(
            _generate_shortened,
            shortened_length,
        ),
    )
    counter = Column(
        BigInteger,
        nullable=False,
        default=0,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )
    user: Mapped["UserModel"] = relationship(
        back_populates="links",
    )

    @classmethod
    def get_cond_list(cls, **kwargs) -> list[BinaryExpression]:
        user: UserModel | None = kwargs.get("user")

        cond_list: list[BinaryExpression] = []
        if user is not None:
            cond_list.append(cls.user_id == user.id)

        return cond_list

    @staticmethod
    def get_select_in_load() -> list[Load]:
        return [selectinload(LinkModel.user)]


class SecretMessageModel(Base):
    __tablename__ = "secret_messages"

    url_length: int = 128

    text = Column(
        TEXT,
        nullable=False,
    )
    visit_counter = Column(
        BIGINT,
        nullable=False,
        default=0,
    )
    ip_address = Column(
        VARCHAR(
            length=64,
        ),
        nullable=False,
    )
    url = Column(
        VARCHAR(
            length=128,
        ),
        unique=True,
        default=partial(
            hasher.get_random_string,
            url_length,
        ),
        nullable=False,
    )


class AuthSessionModel(Base):
    __tablename__ = "auth_sessions"

    key_length: int = 32
    cookie_expiration_time: int = 14 * 24 * 60 * 60

    key = Column(
        VARCHAR(
            length=key_length,
        ),
        unique=True,
        default=partial(
            hasher.get_random_string,
            key_length,
            allowed_chars="abcdefghijklmnopqrstuvwxyz",
        ),
        nullable=False,
    )
    ip_address = Column(
        VARCHAR(
            length=64,
        ),
        nullable=False,
    )
    expired = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )
    user: Mapped["UserModel"] = relationship(
        back_populates="active_sessions",
    )

    @property
    def valid(self) -> bool:
        if self.expired:
            return False

        final_date = self.created_at.replace(tzinfo=UTC) + timedelta(seconds=self.cookie_expiration_time)
        return final_date > datetime.now(tz=UTC)

    @staticmethod
    def get_select_in_load() -> list[Load]:
        return [selectinload(AuthSessionModel.user)]

    @classmethod
    async def do_expire(cls, session: AsyncSession, key: str, /) -> None:
        statement: Update = update(AuthSessionModel).where(AuthSessionModel.key == key).values(expired=True)

        await session.execute(statement)
        await session.commit()
