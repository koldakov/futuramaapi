# import pytest
# from pytest_bdd import scenario, then, when
# from pytest_bdd.parsers import parse
#
# from tests.helpers.enteties import EntityTestClient, get_entity_test_client
#
#
# @scenario(
#     "entities.feature",
#     "Get entity",
# )
# @pytest.mark.anyio
# async def test_get_entity():
#     pass
#
#
# @when(
#     parse("The user requests the {test_client} with id {entity_id}"),
#     converters={
#         "test_client": lambda v: get_entity_test_client(v),
#     },
#     target_fixture="request_result",
# )
# @pytest.mark.anyio
# async def request_entity(test_client: EntityTestClient, entity_id: int):
#     from futuramaapi.main import app
#     from httpx import AsyncClient
#     from httpx import ASGITransport
#     transport = ASGITransport(app)
#     async with AsyncClient(transport=transport, base_url="http://test") as ac:
#         response = await ac.get("/api/characters/1")
#         return response.json()
#     # return test_client.get(entity_id=entity_id)
#
#
# @then(
#     parse("The FuturamaAPI server responds with the {test_client}"),
#     converters={
#         "test_client": lambda v: get_entity_test_client(v),
#     },
# )
# @pytest.mark.anyio
# async def response_entity(request_result, test_client: EntityTestClient):
#     res = await request_result
#     response: test_client.entity = test_client.entity(**res)
#     assert response.id == 1
