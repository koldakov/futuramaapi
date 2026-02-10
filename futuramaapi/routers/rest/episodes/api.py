from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.db import INT32
from futuramaapi.db.session import get_async_session
from futuramaapi.routers.exceptions import NotFoundResponse
from futuramaapi.routers.services.episodes.get_episode import (
    GetEpisodeResponse,
    GetEpisodeService,
)
from futuramaapi.routers.services.episodes.list_episodes import (
    ListEpisodesResponse,
    ListEpisodesService,
)

router: APIRouter = APIRouter(
    prefix="/episodes",
    tags=["episodes"],
)


@router.get(
    "/{episode_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    response_model=GetEpisodeResponse,
    name="episode",
)
async def get_episode(
    episode_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> GetEpisodeResponse:
    """Retrieve specific episode.

    This endpoint allows you to retrieve detailed information about a specific Futurama episode by providing its
    unique ID. The response will include essential details such as the episode name, air date, duration, season,
    production ID, broadcast ID, and other relevant information.

    Can be used to get in-depth information about a particular
    episode of Futurama.
    """
    service: GetEpisodeService = GetEpisodeService(pk=episode_id)
    return await service(session)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[ListEpisodesResponse],
    name="episodes",
)
async def get_episodes() -> Page[ListEpisodesResponse]:
    """Retrieve episodes.

    This endpoint provides a paginated list of Futurama episodes, offering a comprehensive overview
    of the entire series.

    Can be used to access a collection of episode names, air dates, seasons, durations,
    and other relevant details. It's particularly useful for those who want to explore the entire catalog of Futurama
    episodes or implement features such as episode browsing on your site.
    """
    service: ListEpisodesService = ListEpisodesService()
    return await service()
