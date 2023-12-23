from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_storages import StorageImage
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from sqlalchemy import select
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.configs import settings
from app.repositories.models import Character as CharacterModel
from app.repositories.models import (
    CharacterGender,
    CharacterStatus,
)


class Character(BaseModel):
    id: int
    name: str
    gender: CharacterGender
    status: CharacterStatus
    created_at: datetime = Field(alias="createdAt")
    image: Optional[HttpUrl]

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
        return HttpUrl.build(
            scheme="https",
            host=settings.trusted_host,
            path=f"{settings.static}/{value._name}",  # noqa
        )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    def __init__(self, request: Request = None, **data: Any):
        self.request = request
        super().__init__(**data)


async def get_character(
    character_id: int,
    session: AsyncSession,
    /,
) -> Character:
    cursor: Result = await session.execute(
        select(CharacterModel).where(CharacterModel.id == character_id)
    )
    try:
        result: CharacterModel = cursor.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Character.model_validate(result)


async def process_get_character(
    character_id: int,
    session: AsyncSession,
    /,
) -> Character:
    return await get_character(character_id, session)


async def process_get_characters(session: AsyncSession, /) -> Page[Character]:
    return await paginate(
        session,
        select(CharacterModel).order_by(CharacterModel.created_at),
    )
