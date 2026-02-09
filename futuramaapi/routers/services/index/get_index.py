from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, ClassVar, Final, NamedTuple

from aiocache import cached
from sqlalchemy import Result, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from futuramaapi.repositories.models import CharacterModel, RequestsCounterModel, SystemMessage, UserModel
from futuramaapi.routers.services import BaseTemplateService

_TOTAL_REQUESTS_TTL: Final[int] = 60 * 60


class _CachedTotalRequest(NamedTuple):
    value: int
    cached_at: datetime

    @property
    def ttl(self) -> int:
        elapsed: float = (datetime.now(UTC) - self.cached_at).total_seconds()
        return max(0, _TOTAL_REQUESTS_TTL - int(elapsed))


@cached(ttl=_TOTAL_REQUESTS_TTL, key="total-requests")
async def _get_total_requests(session: AsyncSession, /) -> _CachedTotalRequest:
    statement = select(func.coalesce(func.sum(RequestsCounterModel.counter), 0))
    result = await session.execute(statement)
    value: int = result.scalar() or 0

    return _CachedTotalRequest(
        value=value,
        cached_at=datetime.now(UTC),
    )


class GetIndexService(BaseTemplateService):
    template_name: ClassVar[str] = "index.html"

    async def __get_user_count(self) -> int:
        result: Result = await self.session.execute(func.count(UserModel.id))
        return result.scalar()

    async def __get_characters(self) -> Sequence[CharacterModel]:
        statement: Select[tuple[CharacterModel]] = select(CharacterModel).limit(12).order_by(CharacterModel.id.asc())
        return (await self.session.execute(statement)).scalars().all()

    async def __get_system_messages(self) -> Sequence[SystemMessage]:
        statement: Select[tuple[SystemMessage]] = select(SystemMessage)
        return (await self.session.execute(statement)).scalars().all()

    async def get_context(self, *args, **kwargs) -> dict[str, Any]:
        cached_total_request: _CachedTotalRequest = await _get_total_requests(self.session)
        return {
            "user_count": await self.__get_user_count(),
            "characters": await self.__get_characters(),
            "total_api_requests": {
                "cache": {
                    "value": cached_total_request.value,
                    "cached_at": cached_total_request.cached_at,
                    "ttl": cached_total_request.ttl,
                },
            },
            "system_messages": await self.__get_system_messages(),
        }
