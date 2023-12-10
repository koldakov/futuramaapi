from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.episodes import (
    Episode,
    process_get_episode,
    process_get_episodes,
)

router = APIRouter(prefix="/episodes")


@router.get(
    "/{episode_id}",
    status_code=status.HTTP_200_OK,
    response_model=Episode,
    name="episode",
)
async def get_episode(
    episode_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Episode:
    return await process_get_episode(episode_id, session)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Page[Episode],
    name="episodes",
)
async def get_episodes(
    session: AsyncSession = Depends(get_async_session),
) -> Page[Episode]:
    return await process_get_episodes(session)
