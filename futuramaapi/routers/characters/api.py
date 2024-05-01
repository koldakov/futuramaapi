from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session

from .schemas import Character

router = APIRouter(prefix="/characters")


@router.get(
    "/{character_id}",
    status_code=status.HTTP_200_OK,
    response_model=Character,
    name="character",
)
async def get_character(
    character_id: int,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Character:
    """Retrieve specific character.

    This endpoint enables users to retrieve detailed information about a specific Futurama character by providing
    their unique ID. The response will include essential details such as the character's name, status,
    gender, species, image, and other relevant details.

    Can be used to utilize this endpoint to obtain in-depth insights
    into a particular character from the Futurama universe.
    """
    return await Character.get(session, character_id)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[Character],
    name="characters",
)
async def get_characters(
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Page[Character]:
    """Retrieve characters.

    Explore advanced filtering options in our API documentation by checking out the variety of query parameters
    available.

    Also, you can include filtering in requests.
    Use the "!" symbol for logical negation in filtering. For example, If you want to retrieve all aliens with
    known gender and known status, your request would be
    `/api/characters/?gender=!unknown&status=!unknown&species=alien`.
    Check query Parameters to more info.
    """
    return await Character.paginate(session)
