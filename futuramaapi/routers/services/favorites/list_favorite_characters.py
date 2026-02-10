from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from futuramaapi.db.models import CharacterModel, FavoriteCharacterModel
from futuramaapi.routers.services import BaseUserAuthenticatedService
from futuramaapi.routers.services.characters.get_character import GetCharacterResponse


class ListFavoriteCharactersResponse(GetCharacterResponse): ...


class ListFavoriteCharacters(BaseUserAuthenticatedService[Page[ListFavoriteCharactersResponse]]):
    @property
    def statement(self):
        return (
            select(CharacterModel)
            .join(
                FavoriteCharacterModel,
                FavoriteCharacterModel.character_uuid == CharacterModel.uuid,
            )
            .where(FavoriteCharacterModel.user_uuid == self.user.uuid)
        )

    async def process(self, *args, **kwargs) -> Page[ListFavoriteCharactersResponse]:
        return await paginate(
            self.session,
            self.statement,
        )
