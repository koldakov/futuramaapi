from datetime import date, datetime

from fastapi import HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel, ConfigDict, Field, computed_field
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.models import (
    Episode as EpisodeModel,
    EpisodeDoesNotExist,
)
from app.services.base import EpisodeBase


class SeasonEpisode(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Episode(EpisodeBase):
    air_date: date | None = Field(alias="airDate")
    duration: int | None
    created_at: datetime = Field(alias="createdAt")
    season: SeasonEpisode

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

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
    episode_id: int,
    session: AsyncSession,
    /,
) -> Episode:
    try:
        episode: EpisodeModel = await EpisodeModel.get(session, episode_id)
    except EpisodeDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Episode.model_validate(episode)


async def process_get_episode(
    episode_id: int,
    session: AsyncSession,
    /,
) -> Episode:
    return await get_episode(episode_id, session)


async def process_get_episodes(session: AsyncSession, /) -> Page[Episode]:
    return await paginate(
        session,
        select(EpisodeModel)
        .order_by(EpisodeModel.id)
        .options(selectinload(EpisodeModel.season)),
    )
