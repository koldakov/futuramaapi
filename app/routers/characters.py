from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.base import OrderByDirection
from app.repositories.models import (
    Character as CharacterModel,
)
from app.repositories.models import (
    CharacterGenderFilter,
    CharacterSpeciesFilter,
    CharacterStatusFilter,
)
from app.repositories.sessions import get_async_session
from app.services.characters import (
    Character,
    process_get_character,
    process_get_characters,
)

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
    return await process_get_character(character_id, session)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Page[Character],
    name="characters",
)
async def get_characters(  # noqa: PLR0913
    gender: CharacterGenderFilter | None = None,
    character_status: Annotated[
        CharacterStatusFilter | None,
        Query(alias="status"),
    ] = None,
    species: CharacterSpeciesFilter | None = None,
    order_by: Annotated[
        CharacterModel.order_by | None,
        Query(alias="orderBy"),
    ] = CharacterModel.order_by.ID,
    direction: Annotated[
        OrderByDirection | None,
        Query(alias="orderByDirection"),
    ] = OrderByDirection.ASC,
    query: Annotated[
        str | None,
        Query(
            alias="query",
            description="Name search query.",
            max_length=128,
        ),
    ] = None,
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
    return await process_get_characters(
        session,
        gender=gender,
        character_status=character_status,
        species=species,
        order_by=order_by,
        direction=direction,
        query=query,
    )
