from enum import Enum
from typing import List

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import UnaryExpression

_Base = declarative_base()


class OrderByDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class OrderBy(Enum):
    ID = "id"
    CREATED_AT = "createdAt"


class Base[T, U](_Base):
    __abstract__ = True
    order_by: U = OrderBy

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
        ...

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
