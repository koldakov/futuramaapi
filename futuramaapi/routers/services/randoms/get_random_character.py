from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.repositories.models import CharacterModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services import BaseService
from futuramaapi.routers.services.characters.get_character import GetCharacterResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GetRandomCharacterResponse(GetCharacterResponse):
    pass


class GetRandomCharacterService(BaseService):
    @property
    def statement(self) -> Select[tuple[CharacterModel]]:
        return select(CharacterModel).order_by(func.random()).limit(1)

    async def __call__(self, *args, **kwargs) -> GetRandomCharacterResponse:
        session: AsyncSession
        async with session_manager.session() as session:
            try:
                result: CharacterModel = (await session.execute(self.statement)).scalars().one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

        return GetRandomCharacterResponse.model_validate(result)
