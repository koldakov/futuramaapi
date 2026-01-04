from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from futuramaapi.api_clients import BaseClient, HTTPXClient


class BaseTaskService[T: Mapping[str, Any]](ABC):
    def __init__(
        self,
        *,
        api_client: BaseClient | None = None,
    ) -> None:
        self._api: BaseClient = api_client or HTTPXClient()

    @property
    def api(self) -> BaseClient:
        return self._api

    @abstractmethod
    async def process(self, *args, **kwargs) -> T: ...

    async def __call__(self, *args, **kwargs) -> T:
        async with self._api:
            return await self.process(*args, **kwargs)
