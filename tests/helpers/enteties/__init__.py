import typing

from .characters import CharactersTestClient
from .episodes import EpisodesTestClient
from .seasons import SeasonsTestClient

EntityTestClient = CharactersTestClient | EpisodesTestClient | SeasonsTestClient

ENTITY_TEST_CLIENT_MAP: dict[str, type[EntityTestClient]] = {
    _class.entity_name: _class for _class in typing.get_args(EntityTestClient)
}


def get_entity_test_client(name: str, /) -> EntityTestClient:
    return ENTITY_TEST_CLIENT_MAP[name]()
