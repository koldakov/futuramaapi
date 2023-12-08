from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_storages import StorageImage
from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator
from sqlalchemy import select
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession

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
    created_at: datetime
    image: Optional[HttpUrl]

    @field_validator("image", mode="before")
    @classmethod
    def make_url(cls, value: StorageImage) -> HttpUrl:
        """Makes URL from DB path.

        Currently, will return None for all URLs, cause to generate a URL we need a request.

        Args:
            value (fastapi_storages.StorageImage): Image field.

        Returns: None. TODO: propagate request to generate a proper URL
        """
        return None

    model_config = ConfigDict(from_attributes=True)

    def __init__(self, request: Request = None, **data: Any):
        self.request = request
        super().__init__(**data)


async def process_get_character(
    character_id: int,
    session: AsyncSession,
) -> Character:
    cursor: Result = await session.execute(
        select(CharacterModel).where(CharacterModel.id == character_id)
    )
    try:
        result: CharacterModel = cursor.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Character.model_validate(result)


async def process_get_characters(session: AsyncSession) -> Page[Character]:
    return await paginate(
        session,
        select(CharacterModel).order_by(CharacterModel.created_at),
    )
