from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.episodes import (
    Episode,
    process_get_episode,
)

router = APIRouter(prefix="/episodes")


@router.get(
    "/{episode_id}",
    status_code=status.HTTP_200_OK,
    response_model=Episode,
)
async def get_episode(
    episode_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Episode:
    return await process_get_episode(episode_id, session)
