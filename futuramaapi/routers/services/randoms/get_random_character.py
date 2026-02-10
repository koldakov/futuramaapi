from sqlalchemy import Select, func, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.db.models import CharacterModel
from futuramaapi.routers.services import BaseSessionService, NotFoundError
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
            raise NotFoundError() from None

        return GetRandomCharacterResponse.model_validate(result)
