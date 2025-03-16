from asyncio import sleep
from collections.abc import AsyncGenerator
from datetime import datetime
from random import randint

from fastapi import Request
from pydantic import Field
from sqlalchemy.ext.asyncio.session import AsyncSession
from sse_starlette import EventSourceResponse, ServerSentEvent

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.routers.characters.schemas import Character

MIN_COORDINATE: int = 0
MAX_COORDINATE: int = 2**6


class CharacterNotification(BaseModel):
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

    item: Character
    notification: Notification

    @classmethod
    async def get_move(cls, request: Request, character: Character, /) -> AsyncGenerator[ServerSentEvent]:
        while True:
            if await request.is_disconnected():
                # Can be removed. Do not trust lib, force connection close.
                break

            yield ServerSentEvent(
                data=cls(
                    item=character,
                    notification=cls.Notification(
                        x=randint(MIN_COORDINATE, MAX_COORDINATE),  # noqa: S311
                        y=randint(MIN_COORDINATE, MAX_COORDINATE),  # noqa: S311
                    ),
                ).model_dump()
            )
            await sleep(
                randint(1, 3),  # noqa: S311
            )

    @classmethod
    async def from_request(cls, id_: int, request: Request, session: AsyncSession, /) -> EventSourceResponse:
        character: Character = await Character.get(session, id_)
        return EventSourceResponse(cls.get_move(request, character))
