from datetime import datetime

from fastapi import HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.models import Episode as EpisodeModel


class Episode(BaseModel):
    id: int
    name: str
    air_date: datetime = Field(serialization_alias="airDate")
    duration: int | None
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


async def process_get_episode(
    character_id: int,
    session: AsyncSession,
    /,
) -> Episode:
    cursor: Result = await session.execute(
        select(EpisodeModel).where(EpisodeModel.id == character_id)
    )
    try:
        result: EpisodeModel = cursor.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Episode.model_validate(result)


async def process_get_episodes(session: AsyncSession, /) -> Page[Episode]:
    return await paginate(
        session,
        select(EpisodeModel).order_by(EpisodeModel.id),
    )
