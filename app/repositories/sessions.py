from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.configs import settings

async_engine = create_async_engine(
    settings.database_url,
    echo=True,
    future=True,
)


async def get_async_session() -> AsyncSession:
    async_session = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
