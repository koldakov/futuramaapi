from typing import Literal

from pydantic import Field

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import CharacterModel
from futuramaapi.routers.services.characters.get_character import GetCharacterResponse

from ._base import (
    DoesNotExistCallbackResponse,
    GetItemCallbackTaskService,
)


class GetCharacterCallbackResponse(BaseModel):
    class CharacterItem(GetCharacterResponse):
        pass

    kind: Literal["Character"] = Field(
        "Character",
        alias="type",
        description="Requested Object type.",
    )
    item: CharacterItem | DoesNotExistCallbackResponse


class GetCharacterCallbackTaskService(GetItemCallbackTaskService):
    model_class = CharacterModel
    response_class = GetCharacterCallbackResponse
