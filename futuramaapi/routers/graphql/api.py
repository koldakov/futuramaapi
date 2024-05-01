import strawberry
from strawberry.fastapi import GraphQLRouter

from .dependencies import get_context
from .schemas import Query

schema = strawberry.Schema(Query)

router = GraphQLRouter(
    schema,
    path="/graphql",
    context_getter=get_context,
    include_in_schema=False,
)
