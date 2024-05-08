from abc import ABC, abstractmethod
from enum import StrEnum
from functools import cached_property
from typing import Any, ClassVar, Literal

from fastapi.testclient import TestClient

from futuramaapi.core import settings
from futuramaapi.main import app
from futuramaapi.pydantic._base import BaseModel


class EntityName(StrEnum):
    character = "character"
    episode = "episode"
    season = "season"


class TestClientBase(ABC):
    entity_name: ClassVar[EntityName]
    entity: ClassVar[type[BaseModel]]

    @property
    def protocol(self) -> Literal["http", "https"]:
        return "https"

    @property
    def entity_name_plural(self) -> str:
        return f"{self.entity_name}s"

    @abstractmethod
    def assert_response(self, data: dict[str, Any], /) -> None: ...

    @property
    def headers(self) -> dict[str, str]:
        return {
            "host": settings.trusted_host,
            "x-forwarded-proto": self.protocol,
            "x-forwarded-port": "443",
        }

    @property
    def path_base(self) -> str:
        return "api"

    @cached_property
    def client(self) -> TestClient:
        return TestClient(
            app,
            base_url=f"{self.protocol}://{settings.trusted_host}",
            headers=self.headers,
        )

    def get(self, *, entity_id: int | None) -> dict[str, Any]:
        path: str = f"{self.path_base}/{self.entity_name_plural}"
        if entity_id is not None:
            path += f"/{entity_id}"
        response = self.client.get(path)
        return response.json()
