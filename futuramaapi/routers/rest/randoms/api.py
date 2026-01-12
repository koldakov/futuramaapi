from fastapi import APIRouter, status

from futuramaapi.routers.exceptions import NotFoundResponse
from futuramaapi.routers.services.randoms.get_random_character import (
    GetRandomCharacterResponse,
    GetRandomCharacterService,
)
from futuramaapi.routers.services.randoms.get_random_episode import (
    GetRandomEpisodeResponse,
    GetRandomEpisodeService,
)
from futuramaapi.routers.services.randoms.get_random_season import (
    GetRandomSeasonResponse,
    GetRandomSeasonService,
)

router: APIRouter = APIRouter(
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
    response_model=GetRandomCharacterResponse,
    name="random_character",
)
async def get_random_character() -> GetRandomCharacterResponse:
    """Retrieve random character.

    This endpoint allows users to retrieve detailed information about a randomly selected Futurama character.
    The response includes essential details such as the character's name, status, gender, species, image,
    and other relevant attributes.

    Can be used to discover and explore random characters from the Futurama universe,
    offering a fun and engaging way to learn about different personalities in the series.
    """
    service: GetRandomCharacterService = GetRandomCharacterService()
    return await service()


@router.get(
    "/episode",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    response_model=GetRandomEpisodeResponse,
    name="random_episode",
)
async def get_random_episode() -> GetRandomEpisodeResponse:
    """Retrieve random episode.

    This endpoint allows users to retrieve detailed information about a randomly selected Futurama episode.
    The response includes essential details such as the episode's title, season, episode number, air date, synopsis,
    and other relevant information.

    Perfect for when you're not sure which Futurama episode to watch - use this endpoint to get a randomly
    selected episode and dive right in.
    """
    service: GetRandomEpisodeService = GetRandomEpisodeService()
    return await service()


@router.get(
    "/season",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    response_model=GetRandomSeasonResponse,
    name="random_season",
)
async def get_random_season() -> GetRandomSeasonResponse:
    """Retrieve random season.

    This endpoint allows users to retrieve information about a randomly selected season from the Futurama series.
    The response includes key details such as the season number, list of episodes, and other relevant metadata.

    Great for when you can't decide where to start—use this endpoint to randomly pick a season and enjoy a
    fresh batch of Futurama episodes.
    """
    service: GetRandomSeasonService = GetRandomSeasonService()
    return await service()
