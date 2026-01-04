from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from futuramaapi.api_clients import BaseClient, HTTPXClient
from futuramaapi.helpers.pydantic import BaseModel


class BaseTaskService[T: Mapping[str, Any]](BaseModel, ABC):
    def __init__(
        self,
        *,
        api_client: BaseClient | None = None,
        **data: Any,
    ) -> None:
        super().__init__(**data)

        self._api: BaseClient = api_client or HTTPXClient()

    @property
    def api(self) -> BaseClient:
        return self._api

    @abstractmethod
    async def process(self, *args, **kwargs) -> T: ...

    async def __call__(self, *args, **kwargs) -> T:
        async with self._api:
            return await self.process(*args, **kwargs)
