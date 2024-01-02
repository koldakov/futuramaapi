from typing import List

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base

_Base = declarative_base()


class Base(_Base):
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
    ):
        ...
