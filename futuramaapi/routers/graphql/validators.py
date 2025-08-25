from typing import Any

from strawberry import Info
from strawberry.extensions.field_extension import AsyncExtensionResolver, FieldExtension


class LimitsRule(FieldExtension):
    @staticmethod
    def validate_range(name: str, value: int, min_: int, max_: int, /) -> None:
        if not min_ <= value <= max_:
            raise ValueError(f"{name} can be more than {min_} and less than {max_}")

    def validate_limits(self, kwargs: dict):
        for limit in ["limit", "offset"]:
            self.validate_range(limit, kwargs[limit], 0, 50)

    async def resolve_async(
        self,
        next_: AsyncExtensionResolver,
        source: Any,
        info: Info,
        **kwargs,
    ):
        self.validate_limits(kwargs)

        return await next_(source, info, **kwargs)
