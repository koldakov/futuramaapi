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
    """Retrieve specific episode.

    This endpoint allows you to retrieve detailed information about a specific Futurama episode by providing its
    unique ID. The response will include essential details such as the episode name, air date, duration, season,
    production ID, broadcast ID, and other relevant information.

    Can be used to get in-depth information about a particular
    episode of Futurama.
    """
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
    """Retrieve episodes.

    This endpoint provides a paginated list of Futurama episodes, offering a comprehensive overview
    of the entire series.

    Can be used to access a collection of episode names, air dates, seasons, durations,
    and other relevant details. It's particularly useful for those who want to explore the entire catalog of Futurama
    episodes or implement features such as episode browsing on your site.
    """
    return await process_get_episodes(session)
