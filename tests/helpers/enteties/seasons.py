from typing import Any

from futuramaapi.routers.seasons.schemas import Season

from ._base import EntityName, TestClientBase


class SeasonsTestClient(TestClientBase):
    entity_name = EntityName.season
    entity = Season

    def assert_response(self, data: dict[str, Any], /) -> None:
        pass
