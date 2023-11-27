from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.characters import Character, process_get_character

router = APIRouter(prefix="/characters")


@router.get(
    "/{character_id}",
    status_code=status.HTTP_200_OK,
    response_model=Character,
)
async def get_character(
    character_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Character:
    return await process_get_character(character_id, session)
