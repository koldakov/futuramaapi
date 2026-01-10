from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from futuramaapi.repositories.models import SeasonModel
from futuramaapi.routers.services._base import BaseSessionService
from futuramaapi.routers.services.seasons.get_season import GetSeasonResponse


class ListSeasonsResponse(GetSeasonResponse):
    pass


class ListSeasonsService(BaseSessionService[Page[ListSeasonsResponse]]):
    @property
    def statement(self) -> Select:
        return select(SeasonModel).filter().options(selectinload(SeasonModel.episodes))

    async def process(self, *args, **kwargs) -> Page[ListSeasonsResponse]:
        return await paginate(
            self.session,
            self.statement,
        )
