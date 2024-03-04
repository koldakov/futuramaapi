from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_storages import StorageImage
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core import settings
from app.repositories.base import OrderByDirection
from app.repositories.models import Character as CharacterModel
from app.repositories.models import (
    CharacterDoesNotExist,
    CharacterGender,
    CharacterGenderFilter,
    CharacterSpecies,
    CharacterSpeciesFilter,
    CharacterStatus,
    CharacterStatusFilter,
)


def build_url(*, path: str | None = None):
    path = f"{settings.static}/{path}" if path else f"{settings.static}"
    return HttpUrl.build(
        scheme="https",
        host=settings.trusted_host,
        path=path,
    )


class Character(BaseModel):
    id: int  # noqa: A003
    name: str
    gender: CharacterGender
    status: CharacterStatus
    species: CharacterSpecies
    created_at: datetime = Field(alias="createdAt")
    image: HttpUrl | None = None

    @field_validator("image", mode="before")
    @classmethod
    def make_url(cls, value: StorageImage | None) -> HttpUrl | None:
        """Makes URL from DB path.

        FastAPI does NOT work properly with proxy, so for now protocol will be hardcoded.
        TODO: propagate forwarded headers, rely on trusted host.

        Args:
            value (fastapi_storages.StorageImage): Image field.

        Returns:
            ``pydantic.HttpUrl`` if Character has an image returns absolute URL to image and ``None`` otherwise.
        """
        if value is None:
            return None
        return build_url(path=value._name)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    def __init__(self, request: Request | None = None, **data: Any):
        self.request = request
        super().__init__(**data)


async def get_character(
    character_id: int,
    session: AsyncSession,
    /,
) -> Character:
    try:
        character: CharacterModel = await CharacterModel.get(session, character_id)
    except CharacterDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
    return Character.model_validate(character)


async def process_get_character(
    character_id: int,
    session: AsyncSession,
    /,
) -> Character:
    return await get_character(character_id, session)


async def process_get_characters(  # noqa: PLR0913
    session: AsyncSession,
    /,
    *,
    gender: CharacterGenderFilter | None = None,
    character_status: CharacterStatusFilter | None = None,
    species: CharacterSpeciesFilter | None = None,
    order_by: CharacterModel.order_by | None = None,
    direction: OrderByDirection | None = None,
    query: str | None = None,
) -> Page[Character]:
    return await paginate(
        session,
        CharacterModel.get_filter_statement(
            order_by=order_by,
            order_by_direction=direction,
            gender=gender,
            character_statusx=character_status,
            species=species,
            query=query,
        ),
    )
