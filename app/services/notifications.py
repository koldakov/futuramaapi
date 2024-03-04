from asyncio import sleep
from datetime import datetime
from random import randint

from fastapi import Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio.session import AsyncSession
from sse_starlette import EventSourceResponse, ServerSentEvent

from app.services.characters import Character, get_character
from app.templates import gnu_translations

MIN_COORDINATE = 0
MAX_COORDINATE = 2**6


class CharacterMove(BaseModel):
    name: str = Field(gnu_translations.gettext("FB00007"))
    x: int = Field(
        description=gnu_translations.gettext("FB00008"),
        ge=MIN_COORDINATE,
        le=MAX_COORDINATE,
    )
    y: int = Field(
        description=gnu_translations.gettext("FB00009"),
        ge=MIN_COORDINATE,
        le=MAX_COORDINATE,
    )
    time: datetime = datetime.now()


async def generate_character_move(
    request: Request,
    character: Character,
    /,
):
    # I don't like infinite loops, please check if range can be used.
    while True:
        if await request.is_disconnected():
            # Can be removed. Do not trust lib, force connection close.
            break

        yield ServerSentEvent(
            data=CharacterMove(
                name=character.name,
                x=randint(MIN_COORDINATE, MAX_COORDINATE),  # noqa: S311
                y=randint(MIN_COORDINATE, MAX_COORDINATE),  # noqa: S311
            ).model_dump()
        )
        await sleep(randint(1, 3))  # noqa: S311


async def process_character_sse(
    character_id: int,
    request: Request,
    session: AsyncSession,
    /,
) -> EventSourceResponse:
    character: Character = await get_character(character_id, session)
    return EventSourceResponse(generate_character_move(request, character))
