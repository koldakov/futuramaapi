import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from pydantic import PostgresDsn
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from futuramaapi.core import settings

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, host: PostgresDsn, /, *, kwargs: dict[str, Any] | None = None) -> None:
        if kwargs is None:
            kwargs = {}

        self.engine: AsyncEngine | None = create_async_engine(str(host), **kwargs)
        self._session_maker: async_sessionmaker[AsyncSession] | None = async_sessionmaker(
            autocommit=False,
            bind=self.engine,
            expire_on_commit=False,
        )
        self.redis_pool: ConnectionPool | None = settings.redis.pool

    async def close(self) -> None:
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        if self.redis_pool is None:
            raise Exception("Redis pool is not initialized")

        await self.engine.dispose()
        await self.redis_pool.aclose()  # type: ignore[attr-defined]

        self.redis_pool = None
        self.engine = None
        self._session_maker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")

        async with self.engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def redis_session(
        self,
    ) -> AsyncIterator[Redis]:
        if self.redis_pool is None:
            raise Exception("Redis pool is not initialized")

        session: Redis = Redis(connection_pool=self.redis_pool)
        try:
            yield session
        except Exception:
            logger.exception("Redis error")
            raise
        finally:
            await session.aclose()  # type: ignore[attr-defined]


session_manager: SessionManager = SessionManager(
    settings.database_url,
    kwargs={
        "echo": True,
    },
)


async def get_async_session():
    async with session_manager.session() as session:
        yield session


async def get_redis_session():
    async with session_manager.redis_session() as session:
        yield session
