from datetime import datetime

from fastapi_storages import StorageImage
from pydantic import HttpUrl, field_validator

from futuramaapi.core import settings
from futuramaapi.mixins.pydantic import BaseModelGetMixin
from futuramaapi.pydantic import BaseModel
from futuramaapi.repositories.models import CharacterModel


class Character(BaseModel, BaseModelGetMixin):
    id: int
    name: str
    gender: CharacterModel.CharacterGender
    status: CharacterModel.CharacterStatus
    species: CharacterModel.CharacterSpecies
    created_at: datetime
    image: HttpUrl | None = None

    @staticmethod
    def get_model() -> type[CharacterModel]:
        return CharacterModel

    @field_validator("image", mode="before")
    @classmethod
    def make_url(cls, value: StorageImage | str | None, /) -> HttpUrl | None:
        if value is None:
            return None
        if isinstance(value, StorageImage):
            return settings.build_url(path=value._name)
        return HttpUrl(value)
