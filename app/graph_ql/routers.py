import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graph_ql.schemas import Query

schema = strawberry.Schema(Query)
router = GraphQLRouter(schema, path="/graphql")
