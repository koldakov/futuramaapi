from asyncio import sleep
from http import HTTPMethod
from typing import Any, ClassVar

from pydantic import Field, HttpUrl
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from futuramaapi.api_clients import RequestData
from futuramaapi.db import Base
from futuramaapi.db.session import session_manager
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.workers.services._base import BaseAPITaskService


class DoesNotExistCallbackResponse(BaseModel):
    id: int = Field(
        description="Requested Object ID.",
    )
    detail: str = Field(
        default="Not found",
        examples=[
            "Not found",
        ],
    )


class GetItemCallbackTaskService(BaseAPITaskService):
    id: int
    delay: int
    callback_url: HttpUrl

    model_class: ClassVar[type[Base]]
    response_class: ClassVar[type[BaseModel]]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session is not initialized")

        return self._session

    @property
    def _statement(self) -> Select[tuple[Base]]:
        return select(self.model_class).where(self.model_class.id == self.id)

    async def _get_item(self) -> dict[str, Any]:
        try:
            obj: Base = (await self.session.execute(self._statement)).scalars().one()
        except NoResultFound:
            return {"item": {"id": self.id}}

        return {"item": obj}

    async def _send(self, callback_response: BaseModel, /) -> None:
        request_data: RequestData = RequestData(
            url=str(self.callback_url),
            method=HTTPMethod.POST,
            json=callback_response.to_dict(),
        )
        await self.api.request(request_data)

    async def _process(self, *args, **kwargs) -> dict[str, Any]:
        await sleep(self.delay)

        callback_response: BaseModel = self.response_class.model_validate(await self._get_item())
        await self._send(callback_response)

        return {}

    async def process(self, *args, **kwargs) -> dict[str, Any]:
        session: AsyncSession
        async with session_manager.session() as session:
            self._session = session
            return await self._process(*args, **kwargs)
