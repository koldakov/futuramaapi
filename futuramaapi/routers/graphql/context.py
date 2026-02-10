from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from strawberry.fastapi import BaseContext

from futuramaapi.db.session import get_async_session


class Context(BaseContext):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

        super().__init__()

    @classmethod
    async def from_dependency(
        cls,
        session: AsyncSession = Depends(get_async_session),  # noqa: B008
    ):
        return cls(session)
