from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page

from futuramaapi.routers.exceptions import NotFoundResponse
from futuramaapi.routers.services.favorites.create_favorite_character import CreateFavoriteCharacterService
from futuramaapi.routers.services.favorites.delete_favorite_character import DeleteFavoriteCharacterService
from futuramaapi.routers.services.favorites.list_favorite_characters import (
    ListFavoriteCharacters,
    ListFavoriteCharactersResponse,
)
from futuramaapi.security import oauth2_scheme

router: APIRouter = APIRouter(
    prefix="/favorites/characters",
    tags=[
        "Favorite Characters",
    ],
)


@router.post(
    "/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
        status.HTTP_409_CONFLICT: {
            "example": "Character is already in favorites",
        },
    },
    name="create_favorite_character",
)
async def create_favorite_character(
    character_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> None:
    """
    Add character to favorites.

    Adds the specified character to the authenticated user's favorites list.

    If the character is already present in favorites, the request will fail
    with a conflict error.

    This endpoint requires authentication.
    """
    service: CreateFavoriteCharacterService = CreateFavoriteCharacterService(
        token=token,
        character_id=character_id,
    )
    await service()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[ListFavoriteCharactersResponse],
    name="list_favorite_characters",
)
async def get_favorite_characters(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Page[ListFavoriteCharactersResponse]:
    """
    Retrieve favorite characters.

    Returns a paginated list of characters added to the current user's favorites.

    You can use standard pagination parameters to control the size and order of the response.
    This endpoint requires authentication and returns only the favorites of the authorized user.

    Check the query parameters section for available pagination options.
    """
    service: ListFavoriteCharacters = ListFavoriteCharacters(token=token)
    return await service()


@router.delete(
    "/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
        status.HTTP_409_CONFLICT: {
            "example": "Character is already in favorites",
        },
    },
    name="delete_favorite_character",
)
async def delete_favorite_character(
    character_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> None:
    """
    Remove character from favorites.

    Removes the specified character from the authenticated user's favorites list.

    If the character does not exist or is not present in the user's favorites,
    the request will fail with a not found error.

    This endpoint requires authentication and performs a destructive operation
    without returning a response body.
    """
    service: DeleteFavoriteCharacterService = DeleteFavoriteCharacterService(
        token=token,
        character_id=character_id,
    )
    await service()
