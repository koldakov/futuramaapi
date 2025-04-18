from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories import INT32, FilterStatementKwargs
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError, NotFoundResponse

from .schemas import Character

router = APIRouter(
    prefix="/characters",
    tags=["characters"],
)


@router.get(
    "/{character_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    response_model=Character,
    name="character",
)
async def get_character(
    character_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Character:
    """Retrieve specific character.

    This endpoint enables users to retrieve detailed information about a specific Futurama character by providing
    their unique ID. The response will include essential details such as the character's name, status,
    gender, species, image, and other relevant details.

    Can be used to utilize this endpoint to obtain in-depth insights
    into a particular character from the Futurama universe.
    """
    try:
        return await Character.get(session, character_id)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[Character],
    name="characters",
)
async def get_characters(  # noqa: PLR0913
    gender: Literal[
        "male",
        "!male",
        "female",
        "!female",
        "unknown",
        "!unknown",
    ]
    | None = None,
    character_status: Annotated[
        Literal[
            "alive",
            "!alive",
            "dead",
            "!dead",
            "unknown",
            "!unknown",
        ]
        | None,
        Query(alias="status"),
    ] = None,
    species: Literal[
        "human",
        "!human",
        "robot",
        "!robot",
        "head",
        "!head",
        "alien",
        "!alien",
        "mutant",
        "!mutant",
        "monster",
        "!monster",
        "unknown",
        "!unknown",
    ]
    | None = None,
    order_by: Annotated[
        Literal["id"] | None,
        Query(alias="orderBy"),
    ] = "id",
    direction: Annotated[
        Literal["asc", "desc"],
        Query(alias="orderByDirection"),
    ] = "asc",
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
    return await Character.paginate(
        session,
        filter_params=FilterStatementKwargs(
            order_by=order_by,
            order_by_direction=direction,
            extra={
                "gender": gender,
                "species": species,
                "status": character_status,
                "query": query,
            },
        ),
    )
