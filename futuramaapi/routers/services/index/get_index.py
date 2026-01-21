from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, ClassVar

from sqlalchemy import Result, Select, func, select

from futuramaapi.repositories.models import CharacterModel, RequestsCounterModel, SystemMessage, UserModel
from futuramaapi.routers.services import BaseTemplateService


class GetIndexService(BaseTemplateService):
    template_name: ClassVar[str] = "index.html"

    async def __get_user_count(self) -> int:
        result: Result = await self.session.execute(func.count(UserModel.id))
        return result.scalar()

    async def __get_characters(self) -> Sequence[CharacterModel]:
        statement: Select[tuple[CharacterModel]] = select(CharacterModel).limit(12).order_by(CharacterModel.id.asc())
        return (await self.session.execute(statement)).scalars().all()

    async def __get_total_requests(self) -> int:
        statement: Select = select(func.coalesce(func.sum(RequestsCounterModel.counter), 0))
        result: Result = await self.session.execute(statement)
        return result.scalar() or 0

    async def __get_system_messages(self) -> Sequence[SystemMessage]:
        statement: Select[tuple[SystemMessage]] = select(SystemMessage)
        return (await self.session.execute(statement)).scalars().all()

    async def __get_last_day_api_requests(self) -> int:
        statement: Select = select(func.sum(RequestsCounterModel.counter)).where(
            RequestsCounterModel.created_at >= datetime.now(tz=UTC) - timedelta(days=1)
        )
        result: Result = await self.session.execute(statement)
        return result.scalar() or 0

    async def get_context(self, *args, **kwargs) -> dict[str, Any]:
        return {
            "user_count": await self.__get_user_count(),
            "characters": await self.__get_characters(),
            "total_api_requests": await self.__get_total_requests(),
            "system_messages": await self.__get_system_messages(),
            "last_day_api_requests": await self.__get_last_day_api_requests(),
        }
