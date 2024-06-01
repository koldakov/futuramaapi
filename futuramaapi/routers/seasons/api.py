from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError, NotFoundResponse

from .schemas import Season

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
    response_model=Season,
    name="season",
)
async def get_season(
    season_id: int,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Season:
    """Retrieve specific season.

    Utilize this endpoint to retrieve detailed information about a specific Futurama season by providing its unique ID.
    The response includes details such as the list of seasons, season ID, and more.

    Can be used to gain in-depth insights into a particular season of Futurama.
    """
    try:
        return await Season.get(session, season_id)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[Season],
    name="seasons",
)
async def get_seasons(
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Page[Season]:
    """Retrieve specific seasons.

    Access a comprehensive list of all Futurama seasons using this endpoint,
    providing users with a complete overview of the series chronological progression.
    The response includes details such as the list of episodes, season ID, and other.

    This endpoint is valuable for those interested in exploring the entirety of Futurama's seasons or implementing
    features like season browsing on your site.
    """
    return await Season.paginate(session)
