from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.characters.schemas import Character
from futuramaapi.routers.episodes.schemas import Episode
from futuramaapi.routers.exceptions import ModelNotFoundError, NotFoundResponse
from futuramaapi.routers.seasons.schemas import Season

router = APIRouter(
    prefix="/random",
    tags=["random"],
)


@router.get(
    "/character",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    response_model=Character,
    name="random_character",
)
async def get_random_character(
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Character:
    """Retrieve random character.

    This endpoint allows users to retrieve detailed information about a randomly selected Futurama character.
    The response includes essential details such as the character's name, status, gender, species, image,
    and other relevant attributes.

    Can be used to discover and explore random characters from the Futurama universe,
    offering a fun and engaging way to learn about different personalities in the series.
    """
    try:
        return await Character.get_random(session)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


@router.get(
    "/episode",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    response_model=Episode,
    name="random_episode",
)
async def get_random_episode(
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Episode:
    """Retrieve random episode.

    This endpoint allows users to retrieve detailed information about a randomly selected Futurama episode.
    The response includes essential details such as the episode's title, season, episode number, air date, synopsis,
    and other relevant information.

    Perfect for when you're not sure which Futurama episode to watch - use this endpoint to get a randomly
    selected episode and dive right in.
    """
    try:
        return await Episode.get_random(session)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


@router.get(
    "/season",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    response_model=Season,
    name="random_season",
)
async def get_random_season(
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Season:
    """Retrieve random season.

    This endpoint allows users to retrieve information about a randomly selected season from the Futurama series.
    The response includes key details such as the season number, list of episodes, and other relevant metadata.

    Great for when you can't decide where to start—use this endpoint to randomly pick a season and enjoy a
    fresh batch of Futurama episodes.
    """
    try:
        return await Season.get_random(session)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
