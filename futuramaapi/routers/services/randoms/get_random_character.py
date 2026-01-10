from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.repositories.models import CharacterModel
from futuramaapi.routers.services import BaseSessionService
from futuramaapi.routers.services.characters.get_character import GetCharacterResponse


class GetRandomCharacterResponse(GetCharacterResponse):
    pass


class GetRandomCharacterService(BaseSessionService[GetRandomCharacterResponse]):
    @property
    def statement(self) -> Select[tuple[CharacterModel]]:
        return select(CharacterModel).order_by(func.random()).limit(1)

    async def process(self, *args, **kwargs) -> GetRandomCharacterResponse:
        try:
            result: CharacterModel = (await self.session.execute(self.statement)).scalars().one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

        return GetRandomCharacterResponse.model_validate(result)
