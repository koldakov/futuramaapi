from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self

from fastapi import HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.base import Base, FilterStatementKwargs, ModelDoesNotExistError

if TYPE_CHECKING:
    from sqlalchemy import Select


class BaseModelGetMixin[Model: BaseModel](ABC):  # type: ignore[valid-type]
    def __init_subclass__(cls):
        """
        Sanity check.
        """
        if not hasattr(cls, "model_validate"):
            raise RuntimeError(f"Class {cls.__name__} should be inherited from ``pydantic.BaseModel``.")

    @classmethod
    @abstractmethod
    def model_validate(
        cls: type[Model],  # type: ignore[name-defined]
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> Model:  # type: ignore[name-defined]
        ...

    @staticmethod
    @abstractmethod
    def get_model() -> type[Base]: ...

    @classmethod
    async def get(cls, session: AsyncSession, id_: int, /) -> Self:
        try:
            obj: Base = await cls.get_model().get(session, id_)
        except ModelDoesNotExistError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
        return cls.model_validate(obj)

    @classmethod
    async def paginate(
        cls,
        session: AsyncSession,
        /,
        offset: int = 20,
        limit: int = 20,
    ) -> Page[Model]:  # type: ignore[name-defined]
        model: type[Base] = cls.get_model()
        statement: Select[tuple[Base]] = model.get_filter_statement(
            FilterStatementKwargs(
                offset=offset,
                limit=limit,
            )
        )

        return await paginate(
            session,
            statement,
        )
