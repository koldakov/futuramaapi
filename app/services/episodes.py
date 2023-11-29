from datetime import datetime

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.models import Episode as EpisodeModel


class Episode(BaseModel):
    id: int
    name: str
    air_date: datetime
    duration: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


async def process_get_episode(
    character_id: int,
    session: AsyncSession,
) -> Episode:
    cursor: Result = await session.execute(
        select(EpisodeModel).where(EpisodeModel.id == character_id)
    )
    try:
        result: EpisodeModel = cursor.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Episode.model_validate(result)
