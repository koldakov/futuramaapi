from typing import Any

from futuramaapi.routers.episodes.schemas import Episode

from ._base import EntityName, TestClientBase


class EpisodesTestClient(TestClientBase):
    entity_name = EntityName.episode
    entity = Episode

    def assert_response(self, data: dict[str, Any], /) -> None:
        pass
