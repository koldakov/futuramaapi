from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.seasons import (
    Season,
    process_get_season,
)

router = APIRouter(prefix="/seasons")


@router.get(
    "/{season_id}",
    status_code=status.HTTP_200_OK,
    response_model=Season,
    name="season",
)
async def get_season(
    season_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Season:
    return await process_get_season(season_id, session)
