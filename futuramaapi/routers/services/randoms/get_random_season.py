from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.repositories.models import SeasonModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services import BaseService
from futuramaapi.routers.services.seasons.get_season import GetSeasonResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GetRandomSeasonResponse(GetSeasonResponse):
    pass


class GetRandomSeasonService(BaseService):
    @property
    def statement(self) -> Select[tuple[SeasonModel]]:
        return select(SeasonModel).options(selectinload(SeasonModel.episodes)).order_by(func.random()).limit(1)

    async def __call__(self, *args, **kwargs) -> GetRandomSeasonResponse:
        session: AsyncSession
        async with session_manager.session() as session:
            try:
                result: SeasonModel = (await session.execute(self.statement)).scalars().one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

        return GetRandomSeasonResponse.model_validate(result)
