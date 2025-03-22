from typing import Any

from futuramaapi.routers.characters.schemas import Character

from ._base import EntityName, TestClientBase


class CharactersTestClient(TestClientBase):
    entity_name = EntityName.character
    entity = Character

    def assert_response(self, data: dict[str, Any], /) -> None:
        pass
