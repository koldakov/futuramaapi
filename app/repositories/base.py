from enum import Enum
from typing import List, Any, Sequence, Tuple, Type

from sqlalchemy import Column, DateTime, Row, select
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base, selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression

_Base = declarative_base()


class OrderByDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class OrderBy(Enum):
    ID = "id"
    CREATED_AT = "createdAt"


class ModelDoesNotExist(Exception):
    """Model Does Not Exist."""


class Base[T, U, F, O](_Base):
    __abstract__ = True
    order_by: U = OrderBy

    created_at = Column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )

    def to_dict(
        self,
        *,
        exclude: List = None,
    ) -> dict:
        if exclude is None:
            exclude = []
        return {
            k: v
            for k, v in self.__dict__.items()
            if not str(k).startswith("_") and str(k) not in exclude
        }

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        id_: int,
        /,
    ) -> T:
        cursor: Result = await session.execute(select(cls).where(cls.id == id_))
        try:
            return cursor.scalars().one()
        except NoResultFound as err:
            raise ModelDoesNotExist() from err

    @staticmethod
    def filter_obj_to_cond(
        obj: F,
        orig: O,
        model_field: Column[str | Enum],
        /,
    ) -> BinaryExpression:
        if obj.name.startswith("NOT_"):
            return model_field != orig[obj.name.split("NOT_", 1)[1]]
        return model_field == orig[obj.name]

    @classmethod
    def get_filter_statement(
        cls,
        *,
        limit: int = None,
        order_by: Type[Enum] = OrderBy.ID,
        order_by_direction: OrderByDirection = OrderByDirection.ASC,
        select_in_load: InstrumentedAttribute = None,
        offset: int = None,
        **kwargs,
    ):
        statement = select(cls)
        statement = statement.order_by(
            cls.get_order_by(
                field=order_by,
                direction=order_by_direction,
            )
        )
        cond_list: List = cls.get_cond_list(**kwargs)
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
    def get_cond_list(cls, **kwargs) -> List[BinaryExpression]:
        return []

    @classmethod
    async def filter(
        cls,
        session: AsyncSession,
        /,
        *,
        limit: int = None,
        order_by: Type[Enum] = None,
        order_by_direction: OrderByDirection = OrderByDirection.ASC,
        select_in_load: InstrumentedAttribute = None,
        **kwargs,
    ) -> Sequence[Row[Tuple[Any, ...] | Any]]:
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
        field: U = OrderBy.ID,
        direction: OrderByDirection = OrderByDirection.ASC,
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
