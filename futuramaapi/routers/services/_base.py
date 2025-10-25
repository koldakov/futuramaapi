from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from futuramaapi.helpers.pydantic import BaseModel


class BaseService(BaseModel, ABC):
    context: dict[str, Any] | None = None

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> BaseModel | Sequence[BaseModel] | None:
        pass
