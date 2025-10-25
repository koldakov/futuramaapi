from abc import ABC

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from futuramaapi.repositories.models import SeasonModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services._base import BaseService
from futuramaapi.routers.services.seasons.get_season import GetSeasonResponse


class ListSeasonResponse(GetSeasonResponse):
    pass


class ListSeasonsService(BaseService, ABC):
    @property
    def statement(self) -> Select:
        return select(SeasonModel).filter().options(selectinload(SeasonModel.episodes))

    async def __call__(self, *args, **kwargs) -> Page[ListSeasonResponse]:
        async with session_manager.session() as session:
            return await paginate(
                session,
                self.statement,
            )
