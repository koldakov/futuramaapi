from enum import Enum
from typing import List

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base

_Base = declarative_base()


class OrderByDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class OrderBy(Enum):
    ID = "id"
    CREATED_AT = "createdAt"


class Base[T](_Base):
    __abstract__ = True

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
