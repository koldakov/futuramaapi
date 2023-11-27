from datetime import datetime

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


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
