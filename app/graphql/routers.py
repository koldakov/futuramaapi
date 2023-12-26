import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graphql.schemas import Query

schema = strawberry.Schema(Query)
router = GraphQLRouter(schema, path="/graphql")
