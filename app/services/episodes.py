from datetime import date, datetime

from fastapi import HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel, ConfigDict, Field, computed_field
from sqlalchemy import select
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.models import Episode as EpisodeModel
from app.services.base import EpisodeBase


class SeasonEpisode(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Episode(EpisodeBase):
    air_date: date | None = Field(serialization_alias="airDate")
    duration: int | None
    created_at: datetime = Field(serialization_alias="createdAt")
    season: SeasonEpisode

    model_config = ConfigDict(from_attributes=True)

    @computed_field(
        alias="broadcastCode",
        examples=[
            "S01E01",
        ],
        return_type=str,
    )
    @property
    def broadcast_code(self) -> str:
        return f"S{self.season.id:02d}E{self.broadcast_number:02d}"


async def get_episode(
    character_id: int,
    session: AsyncSession,
    /,
) -> Episode:
    cursor: Result = await session.execute(
        select(EpisodeModel)
        .where(EpisodeModel.id == character_id)
        .options(selectinload(EpisodeModel.season))
    )
    try:
        result: EpisodeModel = cursor.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Episode.model_validate(result)


async def process_get_episode(
    character_id: int,
    session: AsyncSession,
    /,
) -> Episode:
    return await get_episode(character_id, session)


async def process_get_episodes(session: AsyncSession, /) -> Page[Episode]:
    return await paginate(
        session,
        select(EpisodeModel)
        .order_by(EpisodeModel.id)
        .options(selectinload(EpisodeModel.season)),
    )
