from typing import ClassVar, Self, cast

from sqlalchemy.ext.asyncio.session import AsyncSession
from strawberry.types.field import StrawberryField

from futuramaapi.db import BaseModel, FilterStatementKwargs, ModelDoesNotExistError

from .conversion import ConverterBase, converter


class StrawberryDatabaseMixin:
    model: ClassVar[type[BaseModel]]

    converter: ClassVar[ConverterBase] = converter

    @classmethod
    def get_fields(cls) -> list[StrawberryField]:
        return cls.__strawberry_definition__.fields  # type: ignore[attr-defined]

    @classmethod
    def from_model(cls, instance: BaseModel, /) -> Self:
        return cls.converter.to_strawberry(cls, instance)

    @classmethod
    async def get(cls, session: AsyncSession, id_: int, /) -> Self | None:
        try:
            obj: BaseModel = await cls.model.get(
                session,
                id_,
            )
        except ModelDoesNotExistError:
            return None

        return cls.from_model(obj)

    @classmethod
    async def paginate(cls, session: AsyncSession, kwargs: FilterStatementKwargs, /) -> Self:
        total: int = await cls.model.count(session)
        edges: list[BaseModel] = cast("list[BaseModel]", await cls.model.filter(session, kwargs))

        return cls(
            limit=kwargs.limit,  # type: ignore[call-arg]
            offset=kwargs.offset,  # type: ignore[call-arg]
            total=total,  # type: ignore[call-arg]
            edges=cls.converter.get_edges(cls, edges),  # type: ignore[call-arg]
        )
