from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.base import OrderBy, OrderByDirection
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
    session: AsyncSession = Depends(get_async_session),
) -> Character:
    return await process_get_character(character_id, session)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Page[Character],
    name="characters",
)
async def get_characters(
    gender: Optional[CharacterGenderFilter] = None,
    character_status: Annotated[
        Optional[CharacterStatusFilter],
        Query(alias="status"),
    ] = None,
    species: Optional[CharacterSpeciesFilter] = None,
    order_by: Annotated[
        Optional[OrderBy],
        Query(alias="orderBy"),
    ] = OrderBy.ID,
    direction: Annotated[
        Optional[OrderByDirection],
        Query(alias="orderByDirection"),
    ] = OrderByDirection.ASC,
    query: Annotated[
        str,
        Query(
            alias="query",
            description="Name search query.",
        ),
    ] = None,
    session: AsyncSession = Depends(get_async_session),
) -> Page[Character]:
    """Retrieve characters information.

    Also, you can include filtering in requests. Check query Parameters to more info.
    "!" is logical "NO". For example, if you want to retrieve all aliens,
    who have known gender and known status request will be
    `/api/characters/?gender=!unknown&status=!unknown&species=alien`.
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
