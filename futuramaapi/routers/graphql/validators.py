from typing import Any, ClassVar

from graphql import GRAPHQL_MAX_INT
from strawberry import Info
from strawberry.extensions.field_extension import AsyncExtensionResolver, FieldExtension


class LimitsRule(FieldExtension):
    min_limit: ClassVar[int] = 0
    max_limit: ClassVar[int] = 50
    min_offset: ClassVar[int] = 0

    def _validate_limit(self, limit: int, /) -> None:
        if not self.min_limit <= limit <= self.max_limit:
            raise ValueError(f"limit violation. Allowed range is {self.min_limit}-{self.max_limit}, current={limit}.")

    def _validate_offset(self, offset: int, /) -> None:
        if not self.min_offset <= offset <= GRAPHQL_MAX_INT:
            raise ValueError(
                f"offset violation. Allowed range is {self.min_offset}-{GRAPHQL_MAX_INT}, current={offset}."
            )

    def validate_kwargs(self, kwargs: dict, /) -> None:
        self._validate_limit(kwargs["limit"])
        self._validate_offset(kwargs["offset"])

    async def resolve_async(
        self,
        next_: AsyncExtensionResolver,
        source: Any,
        info: Info,
        **kwargs,
    ):
        self.validate_kwargs(kwargs)

        return await next_(source, info, **kwargs)
