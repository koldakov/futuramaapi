"""
Actually wanted to move this code to ``futuramaapi.routers.graphql.mixins.StrawberryDatabaseMixin``, but happened
as happened, in this case there won't be a need to pass type, cls and so on.
"""

from abc import ABC, abstractmethod
from functools import singledispatch
from typing import TYPE_CHECKING, Any, cast

from fastapi_storages.base import StorageImage
from strawberry.types.base import StrawberryList, StrawberryOptional, has_object_definition
from strawberry.types.enum import EnumDefinition
from strawberry.types.union import StrawberryUnion

from futuramaapi.core import settings
from futuramaapi.repositories import Base

if TYPE_CHECKING:
    from strawberry.types.field import StrawberryField


@singledispatch
def _convert(
    type_: Any,
    data: Any,
    /,
):
    if has_object_definition(type_):
        if hasattr(type(data), "_strawberry_type"):
            type_ = type(data)._strawberry_type
        if hasattr(type_, "from_model"):
            return type_.from_model(data)
        return _convert(type_, data)

    if isinstance(data, StorageImage):
        if data is None:
            return None

        return settings.build_url(path=data._name)

    return data


@_convert.register
def _(type_: StrawberryOptional, data: Any, /):
    if data is None:
        return data

    return _convert(type_.of_type, data)


@_convert.register
def _(type_: StrawberryUnion, data: Any, /):
    for option_type in type_.types:
        if hasattr(option_type, "_pydantic_type"):
            source_type = option_type._pydantic_type
        else:
            source_type = cast(type, option_type)
        if isinstance(data, source_type):
            return _convert(option_type, data)


@_convert.register
def _(type_: EnumDefinition, data: Any, /):
    return data


@_convert.register
def _(type_: StrawberryList, data: Any, /) -> list:
    items: list = []
    for item in data:
        items.append(_convert(type_.of_type, item))

    return items


class ConverterBase(ABC):
    @staticmethod
    @abstractmethod
    def to_strawberry[S](
        cls: type[S],  # noqa: PLW0211
        model_instance: Base,
        /,
    ) -> S: ...

    @staticmethod
    @abstractmethod
    def get_edges[S](
        cls: type[S],  # noqa: PLW0211
        model_instance: list[Base],
        /,
    ) -> list[S] | None: ...


class ModelConverter(ConverterBase):
    @staticmethod
    def to_strawberry[S](
        cls: type[S],  # noqa: PLW0211
        model_instance: Base,
        /,
    ) -> S:
        kwargs: dict = {}

        field: StrawberryField
        for field in cls.__strawberry_definition__.fields:  # type: ignore[attr-defined]
            data: Any = getattr(model_instance, field.python_name, None)
            if field.init:
                kwargs[field.python_name] = _convert(
                    field.type,
                    data,
                )

        return cls(**kwargs)

    @staticmethod
    def get_edges[S](
        cls: type[S],  # noqa: PLW0211
        data: list[Base],
        /,
    ) -> list[S] | None:
        field: StrawberryField = next(f for f in cls.__strawberry_definition__.fields if f.python_name == "edges")  # type: ignore[attr-defined]
        if field.init:
            return _convert(
                field.type,
                data,
            )
        return None


converter: ConverterBase = ModelConverter()
