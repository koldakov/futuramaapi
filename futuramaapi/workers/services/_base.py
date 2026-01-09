from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from futuramaapi.helpers.pydantic import BaseModel


class BaseTaskService(BaseModel, ABC):
    @abstractmethod
    async def __call__(self, *args, **kwargs) -> Mapping[str, Any]:
        pass
