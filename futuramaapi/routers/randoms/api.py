from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.characters.schemas import Character
from futuramaapi.routers.exceptions import ModelNotFoundError, NotFoundResponse

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
