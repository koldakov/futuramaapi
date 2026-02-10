from sqlalchemy import Delete, Result, delete, select

from futuramaapi.db.models import CharacterModel, FavoriteCharacterModel
from futuramaapi.routers.services import BaseUserAuthenticatedService, NotFoundError


class DeleteFavoriteCharacterService(BaseUserAuthenticatedService[None]):
    character_id: int

    @property
    def _statement(self) -> Delete[tuple[FavoriteCharacterModel, CharacterModel]]:
        return delete(FavoriteCharacterModel).where(
            FavoriteCharacterModel.user_uuid == self.user.uuid,
            FavoriteCharacterModel.character_uuid
            == (select(CharacterModel.uuid).where(CharacterModel.id == self.character_id).scalar_subquery()),
        )

    async def process(self, *args, **kwargs) -> None:
        result: Result[tuple[FavoriteCharacterModel]] = await self.session.execute(self._statement)
        if result.rowcount == 0:
            raise NotFoundError("Character not found or not in favorites")

        await self.session.commit()
