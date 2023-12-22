from typing import List

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.models import Season as SeasonModel
from app.services.base import EpisodeBase


class EpisodeSeason(EpisodeBase):
    model_config = ConfigDict(from_attributes=True)


class Season(BaseModel):
    id: int
    episodes: List[EpisodeSeason]

    model_config = ConfigDict(from_attributes=True)


async def process_get_season(
    season_id: int,
    session: AsyncSession,
    /,
) -> Season:
    cursor: Result = await session.execute(
        select(SeasonModel)
        .where(SeasonModel.id == season_id)
        .options(selectinload(SeasonModel.episodes))
    )
    try:
        result: SeasonModel = cursor.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Season.model_validate(result)
