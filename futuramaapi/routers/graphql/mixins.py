from typing import ClassVar, Self, cast

from fastapi_storages.base import StorageImage
from sqlalchemy.ext.asyncio.session import AsyncSession
from strawberry.types.field import StrawberryField

from futuramaapi.core import settings
from futuramaapi.db import Base, FilterStatementKwargs, ModelDoesNotExistError

from .conversion import ConverterBase, converter


class StrawberryDatabaseMixin:
    model: ClassVar[type[Base]]

    converter: ClassVar[ConverterBase] = converter

    @classmethod
    def get_fields(cls) -> list[StrawberryField]:
        return cls.__strawberry_definition__.fields  # type: ignore[attr-defined]

    @staticmethod
    def to_img(field: StorageImage | None, /) -> str | None:
        if field is None:
            return None

        return settings.build_url(path=field._name)

    @classmethod
    def from_model(cls, instance: Base, /) -> Self:
        return cls.converter.to_strawberry(cls, instance)

    @classmethod
    async def get(cls, session: AsyncSession, id_: int, /) -> Self | None:
        try:
            obj: Base = await cls.model.get(
                session,
                id_,
            )
        except ModelDoesNotExistError:
            return None

        return cls.from_model(obj)

    @classmethod
    async def paginate(cls, session: AsyncSession, kwargs: FilterStatementKwargs, /) -> Self:
        total: int = await cls.model.count(session)
        edges: list[Base] = cast("list[Base]", await cls.model.filter(session, kwargs))

        return cls(
            limit=kwargs.limit,  # type: ignore[call-arg]
            offset=kwargs.offset,  # type: ignore[call-arg]
            total=total,  # type: ignore[call-arg]
            edges=cls.converter.get_edges(cls, edges),  # type: ignore[call-arg]
        )
