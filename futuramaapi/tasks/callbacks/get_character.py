from typing import Literal

from fastapi import BackgroundTasks
from pydantic import Field, HttpUrl

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


async def send_get_character_callback(
    background_tasks: BackgroundTasks,
    pk: int,
    delay: int,
    callback_url: HttpUrl,
) -> None:
    service: GetCharacterCallbackTaskService = GetCharacterCallbackTaskService(
        id=pk,
        delay=delay,
        callback_url=callback_url,
    )
    background_tasks.add_task(service)
