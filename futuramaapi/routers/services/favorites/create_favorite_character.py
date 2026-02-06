from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy import Insert, Result, insert, select
from sqlalchemy.exc import IntegrityError

from futuramaapi.repositories.models import CharacterModel, FavoriteCharacterModel
from futuramaapi.routers.services import BaseUserAuthenticatedService, NotFoundError


class CreateFavoriteCharacterService(BaseUserAuthenticatedService[None]):
    character_id: int

    @property
    def _statement(self) -> Insert[tuple[FavoriteCharacterModel]]:
        return insert(FavoriteCharacterModel).values(
            user_uuid=self.user.uuid,
            character_uuid=(
                select(CharacterModel.uuid).where(CharacterModel.id == self.character_id).scalar_subquery()
            ),
        )

    async def process(self) -> None:
        try:
            result: Result[tuple[FavoriteCharacterModel]] = await self.session.execute(self._statement)
        except IntegrityError as err:
            await self.session.rollback()

            if err.orig.sqlstate == UniqueViolationError.sqlstate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Character is already in favorites",
                ) from None
            raise

        if result.rowcount == 0:
            raise NotFoundError("Character not found")

        await self.session.commit()
