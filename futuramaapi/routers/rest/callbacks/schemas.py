from asyncio import sleep
from random import randint
from typing import Literal, Self, cast

from fastapi import BackgroundTasks
from httpx import AsyncClient, Response
from pydantic import Field, HttpUrl
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.routers.exceptions import ModelNotFoundError
from futuramaapi.routers.rest.characters.schemas import Character
from futuramaapi.routers.rest.episodes.schemas import Episode
from futuramaapi.routers.rest.seasons.schemas import Season

MIN_DELAY: int = 5
MAX_DELAY: int = 10


class DoesNotExist(BaseModel):
    id: int = Field(
        description="Requested Object ID.",
    )
    detail: str = Field(
        default="Not found",
        examples=[
            "Not found",
        ],
    )


class CallbackObjectResponse(BaseModel):
    # Can't use type even with noqa: A003, cause native type is being used for a arg typing below.
    kind: Literal["Character", "Episode", "Season"] = Field(
        alias="type",
        description="Requested Object type.",
    )
    item: Character | Episode | Season | DoesNotExist

    @classmethod
    async def from_item(
        cls,
        session: AsyncSession,
        requested_object: type[Character | Episode | Season],
        id_: int,
        /,
    ) -> Self:
        item: Character | Episode | Season | DoesNotExist
        try:
            item = await requested_object.get(session, id_)
        except ModelNotFoundError:
            item = DoesNotExist(
                id=id_,
            )
        return cls(
            type=cast(Literal["Character", "Episode", "Season"], requested_object.__name__),
            item=item,
        )

    async def send_callback(self, url: HttpUrl, /) -> None:
        async with AsyncClient(http2=True) as client:
            callback_response: Response = await client.post(
                f"{url}",
                json=self.to_dict(),
            )
            callback_response.raise_for_status()


class CallbackRequest(BaseModel):
    callback_url: HttpUrl


class CallbackResponse(BaseModel):
    @staticmethod
    def _generate_random_delay() -> int:
        return randint(MIN_DELAY, MAX_DELAY)  # noqa: S311

    delay: int = Field(
        default_factory=_generate_random_delay,
        ge=MIN_DELAY,
        le=MAX_DELAY,
        description="Delay after which the callback will be sent.",
    )

    async def process_background_task(
        self,
        session: AsyncSession,
        requested_object: type[Character | Episode | Season],
        request: CallbackRequest,
        id_: int,
        /,
    ) -> None:
        await sleep(self.delay)
        callback_response: CallbackObjectResponse = await CallbackObjectResponse.from_item(
            session,
            requested_object,
            id_,
        )
        await session.close()
        await callback_response.send_callback(request.callback_url)

    @classmethod
    async def process(
        cls,
        session: AsyncSession,
        requested_object: type[Character | Episode | Season],
        request: CallbackRequest,
        id_: int,
        background_tasks: BackgroundTasks,
        /,
    ) -> Self:
        response: Self = cls()
        background_tasks.add_task(
            response.process_background_task,
            session,
            requested_object,
            request,
            id_,
        )
        return response
