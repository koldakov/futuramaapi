from typing import TYPE_CHECKING, NamedTuple, Self
from uuid import UUID, uuid4

from sqlalchemy import UUID as COLUMN_UUID
from sqlalchemy import Column, DateTime, Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from sqlalchemy.engine.result import Result


class ModelBaseError(Exception): ...


class ModelDoesNotExistError(ModelBaseError): ...


class FilterStatementKwargs(NamedTuple):
    offset: int | None = None
    limit: int | None = None


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

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
    async def count(cls, session: AsyncSession, /) -> int:
        cursor: Result = await session.execute(func.count(cls.id))
        return cursor.scalar()

    @staticmethod
    def get_select_in_load() -> list[Load]:
        return []

    @classmethod
    def get_options(cls) -> list[Load]:
        return [*cls.get_select_in_load()]

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        val: int | str | UUID,
        /,
        *,
        field: InstrumentedAttribute | None = None,
    ) -> Self:
        options: list[Load] = cls.get_options()
        if field is None:
            field = cls.id

        statement: Select = select(cls).where(field == val)
        if options:
            statement = statement.options(*options)

        cursor: Result = await session.execute(statement)
        try:
            return cursor.scalars().one()
        except NoResultFound as err:
            raise ModelDoesNotExistError() from err

    @classmethod
    def get_filter_statement(
        cls,
        kwargs: FilterStatementKwargs,
        /,
    ) -> Select[tuple[Self]]:
        statement: Select[tuple[Base]] = select(cls)

        options: list[Load] = cls.get_options()
        if options:
            statement.options(*options)
        if kwargs.offset is not None:
            statement = statement.offset(kwargs.offset)
        if kwargs.limit is not None:
            statement = statement.limit(kwargs.limit)
        return statement
