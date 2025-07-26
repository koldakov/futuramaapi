from datetime import datetime
from typing import ClassVar

from fastapi_storages import StorageImage
from pydantic import HttpUrl, field_validator

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.mixins.pydantic import BaseModelDatabaseMixin
from futuramaapi.repositories.models import CharacterModel


class Character(BaseModel, BaseModelDatabaseMixin):
    model: ClassVar[type[CharacterModel]] = CharacterModel

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
