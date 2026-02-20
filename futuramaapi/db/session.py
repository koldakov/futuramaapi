import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from futuramaapi.core import settings

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(  # noqa: PLR0913
        self,
        host: PostgresDsn,
        /,
        *,
        echo: bool = False,
        max_overflow: int = settings.pool_max_overflow,
        pool_size: int = settings.pool_size,
        pool_timeout: int = settings.pool_timeout,
        pool_recycle: int = settings.pool_recycle,
        autocommit: bool = False,
        expire_on_commit: bool = False,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            str(host),
            echo=echo,
            max_overflow=max_overflow,
            pool_size=pool_size,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
        )

        self._session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            autocommit=autocommit,
            bind=self.engine,
            expire_on_commit=expire_on_commit,
        )
        self._is_closed: bool = False

    async def close(self) -> None:
        if self._is_closed:
            raise RuntimeError("SessionManager has been closed.")

        await self.engine.dispose()

        self._is_closed = True

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._is_closed:
            raise RuntimeError("SessionManager has been closed.")

        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


session_manager: SessionManager = SessionManager(settings.database_url)


async def get_async_session():
    async with session_manager.session() as session:
        yield session
