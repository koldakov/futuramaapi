from datetime import datetime
from typing import Literal

from pydantic import Field, HttpUrl, field_validator

from futuramaapi.core import settings
from futuramaapi.db.models import CharacterModel
from futuramaapi.helpers import BaseModel

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
        def make_url(cls, value: str | None, /) -> HttpUrl | None:
            if value is None:
                return None
            return settings.build_cdn_url(value)

    kind: Literal["Character"] = Field(
        "Character",
        alias="type",
        description="Requested Object type.",
    )
    item: CharacterItem | DoesNotExistCallbackResponse


class GetCharacterCallbackTaskService(GetItemCallbackTaskService):
    model_class = CharacterModel
    response_class = GetCharacterCallbackResponse
