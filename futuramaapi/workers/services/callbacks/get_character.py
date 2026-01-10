from datetime import datetime
from typing import Literal

from fastapi_storages import StorageImage
from pydantic import Field, HttpUrl, field_validator

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import CharacterModel

from ._base import (
    DoesNotExistCallbackResponse,
    GetItemCallbackTaskService,
)


class GetCharacterCallbackResponse(BaseModel):
    class CharacterItem(BaseModel):
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

    kind: Literal["Character"] = Field(
        "Character",
        alias="type",
        description="Requested Object type.",
    )
    item: CharacterItem | DoesNotExistCallbackResponse


class GetCharacterCallbackTaskService(GetItemCallbackTaskService):
    model_class = CharacterModel
    response_class = GetCharacterCallbackResponse
