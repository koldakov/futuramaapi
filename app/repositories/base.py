from collections.abc import Sequence
from enum import Enum
from typing import TYPE_CHECKING, Any, Self
from uuid import UUID, uuid4

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import UUID as COLUMN_UUID
from sqlalchemy import Column, DateTime, Row, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression

if TYPE_CHECKING:
    from sqlalchemy.engine.result import Result


class OrderByDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class OrderBy(Enum):
    ID = "id"
    CREATED_AT = "createdAt"


class ModelDoesNotExist(Exception):
    """Model Does Not Exist."""


class ModelAlreadyExist(Exception):
    """Model Already Exists"""


class Base(DeclarativeBase):
    __abstract__ = True

    order_by = OrderBy

    model_already_exists: type[ModelAlreadyExist] = ModelAlreadyExist
    model_does_not_exist: type[ModelDoesNotExist] = ModelDoesNotExist

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003

    created_at = Column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )
    uuid = Column(
        COLUMN_UUID(
            as_uuid=True,
        ),
        primary_key=False,
        unique=True,
        nullable=False,
        default=uuid4,
    )

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        val: int | str | UUID,
        /,
        *,
        field: InstrumentedAttribute | None = None,
    ) -> Self:
        if field is None:
            field = cls.id
        statement = select(cls).where(field == val)
        cursor: Result = await session.execute(statement)
        try:
            return cursor.scalars().one()
        except NoResultFound:
            raise cls.model_does_not_exist() from None

    @staticmethod
    def filter_obj_to_cond(
        obj,
        orig,
        model_field: Column[str | Enum],
        /,
    ) -> BinaryExpression:
        if obj.name.startswith("NOT_"):
            return model_field != orig[obj.name.split("NOT_", 1)[1]]
        return model_field == orig[obj.name]

    @classmethod
    def get_filter_statement(  # noqa: PLR0913
        cls,
        *,
        limit: int | None = None,
        order_by=OrderBy.ID,
        order_by_direction=OrderByDirection.ASC,
        select_in_load: InstrumentedAttribute | None = None,
        offset: int | None = None,
        **kwargs,
    ):
        statement = select(cls)
        statement = statement.order_by(
            cls.get_order_by(
                field=order_by,
                direction=order_by_direction,
            )
        )
        cond_list: list = cls.get_cond_list(**kwargs)
        if cond_list:
            statement = statement.where(*cond_list)
        if select_in_load is not None:
            statement = statement.options(selectinload(select_in_load))
        if offset:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return statement

    @classmethod
    def get_cond_list(cls, **kwargs) -> list[BinaryExpression]:
        return []

    @classmethod
    async def filter(  # noqa: A003, PLR0913
        cls,
        session: AsyncSession,
        /,
        *,
        limit: int | None = None,
        order_by=None,
        order_by_direction=OrderByDirection.ASC,
        select_in_load: InstrumentedAttribute | None = None,
        **kwargs,
    ) -> Sequence[Row[tuple[Any, ...] | Any]]:
        if order_by is None:
            order_by = cls.order_by.ID
        statement = cls.get_filter_statement(
            limit=limit,
            order_by=order_by,
            order_by_direction=order_by_direction,
            select_in_load=select_in_load,
            **kwargs,
        )
        cursor: Result = await session.execute(statement)
        return cursor.scalars().all()

    @classmethod
    def get_order_by(
        cls,
        *,
        field=OrderBy.ID,
        direction=OrderByDirection.ASC,
    ) -> UnaryExpression:
        _field: InstrumentedAttribute
        if field is None:
            _field = cls.id
        else:
            _field = cls.__table__.c[field.name.lower()]
        if direction == OrderByDirection.DESC:
            return _field.desc()
        return _field.asc()

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        res = await session.execute(func.count(cls.id))
        return res.scalar()

    @classmethod
    async def add(
        cls,
        session: AsyncSession,
        data,
        /,
        *,
        commit: bool = True,
        extra_fields: dict[
            str,
            Any,
        ]
        | None = None,
    ) -> Self:
        obj: Self = cls(**data.model_dump())
        if extra_fields is not None:
            for name, value in extra_fields.items():
                setattr(obj, name, value)
        session.add(obj)
        if commit is True:
            try:
                await session.commit()
            except IntegrityError as err:
                if err.orig.sqlstate == UniqueViolationError.sqlstate:
                    raise cls.model_already_exists() from None
                raise
        return obj
