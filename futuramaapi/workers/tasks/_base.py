from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class BaseTaskService(ABC):
    @abstractmethod
    async def __call__(self, *args, **kwargs) -> Mapping[str, Any]:
        pass
