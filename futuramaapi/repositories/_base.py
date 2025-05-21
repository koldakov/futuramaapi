import logging
from collections.abc import Callable, Sequence
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Final, Literal, NamedTuple, Self
from uuid import UUID, uuid4

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from sqlalchemy import UUID as COLUMN_UUID
from sqlalchemy import Column, DateTime, Row, Select, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.inspection import Inspectable
from sqlalchemy.orm import DeclarativeBaseNoMeta as _DeclarativeBaseNoMeta
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept as _DeclarativeAttributeIntercept
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import func
from sqlalchemy.sql._typing import _HasClauseElement
from sqlalchemy.sql.elements import BinaryExpression, ColumnElement, SQLCoreOperations, UnaryExpression
from sqlalchemy.sql.roles import ColumnsClauseRole, TypedColumnsClauseRole

from futuramaapi.helpers.pydantic import BaseModel

if TYPE_CHECKING:
    from sqlalchemy.engine.result import Result

logger = logging.getLogger(__name__)

INT32: Final[int] = 2147483647


class ModelBaseError(Exception): ...


class ModelDoesNotExistError(ModelBaseError): ...


class ModelAlreadyExistsError(ModelBaseError): ...


class ModelForeignKeyViolationError(ModelBaseError): ...


class ModelFieldError(ModelBaseError): ...


class FilterStatementKwargs(NamedTuple):
    offset: int | None = None
    limit: int | None = None
    order_by: str | None = "id"
    order_by_direction: Literal["asc", "desc"] = "asc"
    extra: dict | None = None


class DeclarativeBaseNoMeta(_DeclarativeBaseNoMeta):
    pass


class DeclarativeAttributeIntercept(_DeclarativeAttributeIntercept):
    @property
    def select_(
        cls,  # noqa: N805
    ) -> Callable[
        [
            tuple[
                TypedColumnsClauseRole[Any]
                | ColumnsClauseRole
                | SQLCoreOperations[Any]
                | Inspectable[_HasClauseElement[Any]]
                | _HasClauseElement[Any]
                | Any,
                ...,
            ],
            dict[str, Any],
        ],
        Select[Any],
    ]:
        return select


class Base(
    DeclarativeBaseNoMeta,
    metaclass=DeclarativeAttributeIntercept,
):
    __abstract__ = True

    negation: str = "!"

    id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )
    uuid: Mapped[UUID] = mapped_column(
        COLUMN_UUID(
            as_uuid=True,
        ),
        primary_key=False,
        unique=True,
        nullable=False,
        default=uuid4,
    )

    order_by_direction: Literal["asc", "desc"] = "asc"

    @classmethod
    async def count(cls, session: AsyncSession, /) -> int:
        cursor: Result = await session.execute(func.count(cls.id))
        return cursor.scalar()

    @staticmethod
    def get_select_in_load() -> list[Load]:
        return []

    @classmethod
    def get_options(cls) -> list[Load]:
        return cls.get_select_in_load()

    @classmethod
    def get_cond_list(cls, **kwargs) -> list[BinaryExpression]:
        return []

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        val: int | str | UUID,
        /,
        *,
        field: InstrumentedAttribute | None = None,
        extra_where: list[ColumnElement[bool]] | None = None,
    ) -> Self:
        options: list[Load] = cls.get_options()
        if field is None:
            field = cls.id

        where_cond: list = [field == val]
        if extra_where is not None:
            where_cond.extend(extra_where)

        # TODO: I mean fix ignoring
        statement: Select = cls.select_(cls).where(*where_cond)  # type: ignore[call-arg]
        if options:
            statement = statement.options(*options)

        cursor: Result = await session.execute(statement)
        try:
            return cursor.scalars().one()
        except NoResultFound as err:
            raise ModelDoesNotExistError() from err

    @classmethod
    async def get_or_none(
        cls,
        session: AsyncSession,
        val: int | str | UUID,
        /,
        field: InstrumentedAttribute | None = None,
    ) -> Self | None:
        try:
            return await cls.get(session, val, field=field)
        except ModelDoesNotExistError:
            return None

    @classmethod
    def get_order_by(
        cls,
        *,
        field_name: str | None = None,
        direction: Literal["asc", "desc"] = "asc",
    ) -> UnaryExpression:
        field: InstrumentedAttribute
        if field_name is None:
            field = cls.id
        else:
            field = cls.__table__.c[field_name.lower()]

        if direction == "desc":
            return field.desc()
        return field.asc()

    @classmethod
    def get_filter_statement(
        cls,
        kwargs: FilterStatementKwargs,
        /,
    ) -> Select[tuple[Self]]:
        # TODO: I mean fix ignoring
        statement: Select[tuple[Base]] = cls.select_(cls)  # type: ignore[call-arg]
        statement = statement.order_by(
            cls.get_order_by(
                field_name=kwargs.order_by,
                direction=kwargs.order_by_direction,
            )
        )

        cond_list: list = []
        if kwargs.extra is not None:
            cond_list = cls.get_cond_list(**kwargs.extra)
        if cond_list:
            statement = statement.where(*cond_list)
        options: list[Load] = cls.get_options()
        if options:
            statement = statement.options(*options)
        if kwargs.offset is not None:
            statement = statement.offset(kwargs.offset)
        if kwargs.limit is not None:
            statement = statement.limit(kwargs.limit)
        return statement

    @classmethod
    def get_binary_cond(cls, field: Column[str | Enum], value: str, /) -> BinaryExpression:
        if value.startswith(cls.negation):
            return field != value[1:]

        return field == value

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: BaseModel,
        /,
        *,
        commit: bool = True,
        extra_fields: dict[
            str,
            Any,
        ]
        | None = None,
    ) -> Self:
        obj: Self = cls(**data.to_dict(by_alias=False, reveal_secrets=True))
        if extra_fields is not None:
            for name, value in extra_fields.items():
                setattr(obj, name, value)
        session.add(obj)
        if commit is True:
            try:
                await session.commit()
            except IntegrityError as err:
                await session.rollback()

                if err.orig.sqlstate == UniqueViolationError.sqlstate:
                    raise ModelAlreadyExistsError() from None
                elif err.orig.sqlstate == ForeignKeyViolationError.sqlstate:
                    raise ModelForeignKeyViolationError() from None
                raise
        return obj

    @classmethod
    def validate_field(cls, field: str, value: Any, /) -> None:
        try:
            field_: InstrumentedAttribute = getattr(cls, field)
        except AttributeError as err:
            logger.exception(
                "Field does not exist.",
                extra={
                    "data": {
                        "field": field,
                        "err": err,
                        "model": cls,
                    }
                },
            )
            raise ModelFieldError() from None
        if field_.nullable is False and value is None:
            logger.exception(
                "Attempt to assign None to non nullable field.",
                extra={
                    "data": {
                        "field": field,
                        "model": cls,
                    }
                },
            )
            raise ModelFieldError() from None

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        id_: int,
        data: dict,
        /,
    ) -> Self:
        try:
            obj: Self = await cls.get(session, id_)
        except ModelDoesNotExistError:
            raise

        for field, value in data.items():
            if value is not None:
                setattr(obj, field, value)

        await session.commit()

        return obj

    @classmethod
    async def filter(
        cls,
        session: AsyncSession,
        kwargs: FilterStatementKwargs,
        /,
    ) -> Sequence[Row[tuple[Any, ...] | Any]]:
        statement = cls.get_filter_statement(kwargs)
        cursor: Result = await session.execute(statement)
        return cursor.scalars().all()

    @classmethod
    async def get_random(
        cls,
        session: AsyncSession,
        /,
        *,
        extra_where: list[ColumnElement[bool]] | None = None,
    ) -> Self:
        # TODO: Implement extra where
        statement: Select[tuple[Base]] = select(cls).order_by(func.random()).limit(1)
        cursor: Result = await session.execute(statement)
        try:
            return cursor.scalars().one()
        except NoResultFound as err:
            raise ModelDoesNotExistError() from err
