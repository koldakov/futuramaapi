from asyncio import sleep
from typing import TYPE_CHECKING, Literal

from fastapi import BackgroundTasks
from httpx import AsyncClient, Response
from pydantic import Field, HttpUrl
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import CharacterModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services import BaseService
from futuramaapi.routers.services.characters.get_character import Character

from ._base import (
    CallbackRequest,
    CallbackResponse,
    DoesNotExist,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GetCharacterCallbackResponse(BaseModel):
    kind: Literal["Character"] = Field(
        alias="type",
        description="Requested Object type.",
    )
    item: Character | DoesNotExist

    async def send_callback(self, url: HttpUrl, /) -> None:
        async with AsyncClient(http2=True) as client:
            callback_response: Response = await client.post(
                f"{url}",
                json=self.to_dict(),
            )
            callback_response.raise_for_status()


async def _process_background_task(
    delay,
    request: CallbackRequest,
    pk: int,
    /,
) -> None:
    """
    TODO: The code will be much improved when we move to separate service for other instances.
    """
    await sleep(delay)

    session: AsyncSession
    async with session_manager.session() as session:
        try:
            data = (await session.execute(select(CharacterModel).where(CharacterModel.id == pk))).scalars().one()
            data = {
                "item": data,
            }
        except NoResultFound:
            data = {
                "item": {
                    "id": pk,
                },
            }

    data.update({"kind": "Character"})
    response: GetCharacterCallbackResponse = GetCharacterCallbackResponse.model_validate(data)
    await response.send_callback(request.callback_url)


class GetCharacterCallbackService(BaseService):
    request_data: CallbackRequest
    id: int

    async def __call__(self, background_tasks: BackgroundTasks, *args, **kwargs) -> CallbackResponse:
        response: CallbackResponse = CallbackResponse()
        background_tasks.add_task(
            _process_background_task,
            response.delay,
            self.request_data,
            self.id,
        )
        return response
