from datetime import datetime

from fastapi_storages import StorageImage
from pydantic import HttpUrl, field_validator
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.core import settings
from futuramaapi.db.models import CharacterModel
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.routers.services import BaseSessionService, NotFoundError


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


class GetCharacterService(BaseSessionService[GetCharacterResponse]):
    pk: int

    @property
    def statement(self) -> Select[tuple[CharacterModel]]:
        return select(CharacterModel).where(CharacterModel.id == self.pk)

    async def process(self, *args, **kwargs) -> GetCharacterResponse:
        try:
            result: CharacterModel = (await self.session.execute(self.statement)).scalars().one()
        except NoResultFound:
            raise NotFoundError("Character not found") from None

        return GetCharacterResponse.model_validate(result)
