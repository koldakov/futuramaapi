from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from fastapi_storages import StorageImage
from pydantic import HttpUrl, field_validator
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import CharacterModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services import BaseService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GetCharacterResponse(BaseModel):
    id: int
    name: str
    gender: CharacterModel.CharacterGender
    status: CharacterModel.CharacterStatus
    species: CharacterModel.CharacterSpecies
    created_at: datetime
    image: HttpUrl | None = None

    @field_validator("image", mode="before")
    @classmethod
    def make_url(cls, value: StorageImage | str | None, /) -> HttpUrl | None:
        if value is None:
            return None
        if isinstance(value, StorageImage):
            return settings.build_url(path=value._name)
        return HttpUrl(value)


class GetCharacterService(BaseService):
    pk: int

    @property
    def statement(self) -> Select[tuple[CharacterModel]]:
        return select(CharacterModel).where(CharacterModel.id == self.pk)

    async def __call__(self, *args, **kwargs) -> GetCharacterResponse:
        session: AsyncSession
        async with session_manager.session() as session:
            try:
                result: CharacterModel = (await session.execute(self.statement)).scalars().one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found") from None

        return GetCharacterResponse.model_validate(result)
