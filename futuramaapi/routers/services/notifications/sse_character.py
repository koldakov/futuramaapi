from asyncio import sleep
from collections.abc import AsyncGenerator
from datetime import datetime
from random import randint
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, status
from pydantic import Field
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sse_starlette import EventSourceResponse, ServerSentEvent

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import CharacterModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services import BaseService
from futuramaapi.routers.services.characters.get_character import GetCharacterResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio.session import AsyncSession

MIN_COORDINATE: int = 0
MAX_COORDINATE: int = 2**6


class CharacterNotificationResponse(BaseModel):
    class Notification(BaseModel):
        time: datetime = Field(default_factory=datetime.now)
        x: int = Field(
            description="Character X coordinate",
            ge=MIN_COORDINATE,
            le=MAX_COORDINATE,
        )
        y: int = Field(
            description="Character Y coordinate",
            ge=MIN_COORDINATE,
            le=MAX_COORDINATE,
        )

    item: GetCharacterResponse
    notification: Notification


class GetCharacterNotificationService(BaseService):
    pk: int

    async def get_move(self, request: Request, character: CharacterModel, /) -> AsyncGenerator[ServerSentEvent]:
        while True:
            if await request.is_disconnected():
                # Can be removed. Do not trust lib, force connection close.
                break

            yield ServerSentEvent(
                data=CharacterNotificationResponse.model_validate(
                    {
                        "item": character,
                        "notification": {
                            "x": randint(MIN_COORDINATE, MAX_COORDINATE),  # noqa: S311
                            "y": randint(MIN_COORDINATE, MAX_COORDINATE),  # noqa: S311
                        },
                    }
                ).model_dump()
            )
            await sleep(
                randint(1, 3),  # noqa: S311
            )

    @property
    def statement(self) -> Select[tuple[CharacterModel]]:
        return select(CharacterModel).where(CharacterModel.id == self.pk)

    async def __call__(self, request: Request, *args, **kwargs) -> EventSourceResponse:
        session: AsyncSession
        async with session_manager.session() as session:
            try:
                character: CharacterModel = (await session.execute(self.statement)).scalars().one()
            except NoResultFound:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Character with id={self.pk} not found",
                ) from None

        return EventSourceResponse(self.get_move(request, character))
