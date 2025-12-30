from typing import Annotated

from fastapi import APIRouter, Path, status
from fastapi_pagination import Page

from futuramaapi.repositories import INT32
from futuramaapi.routers.exceptions import NotFoundResponse
from futuramaapi.routers.services.seasons.get_season import (
    GetSeasonResponse,
    GetSeasonService,
)
from futuramaapi.routers.services.seasons.list_seasons import (
    ListSeasonsResponse,
    ListSeasonsService,
)

router = APIRouter(
    prefix="/seasons",
    tags=["seasons"],
)


@router.get(
    "/{season_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    response_model=GetSeasonResponse,
    name="season",
)
async def get_season(
    season_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
) -> GetSeasonResponse:
    """Retrieve specific season.

    Utilize this endpoint to retrieve detailed information about a specific Futurama season by providing its unique ID.
    The response includes details such as the list of seasons, season ID, and more.

    Can be used to gain in-depth insights into a particular season of Futurama.
    """
    service: GetSeasonService = GetSeasonService(pk=season_id)
    return await service()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[ListSeasonsResponse],
    name="seasons",
)
async def get_seasons() -> Page[ListSeasonsResponse]:
    """Retrieve specific seasons.

    Access a comprehensive list of all Futurama seasons using this endpoint,
    providing users with a complete overview of the series chronological progression.
    The response includes details such as the list of episodes, season ID, and other.

    This endpoint is valuable for those interested in exploring the entirety of Futurama's seasons or implementing
    features like season browsing on your site.
    """
    service: ListSeasonsService = ListSeasonsService()
    return await service()
