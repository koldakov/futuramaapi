from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from futuramaapi.db.models import EpisodeModel
from futuramaapi.routers.services._base import BaseSessionService
from futuramaapi.routers.services.episodes.get_episode import GetEpisodeResponse


class ListEpisodesResponse(GetEpisodeResponse):
    pass


class ListEpisodesService(BaseSessionService[Page[ListEpisodesResponse]]):
    @property
    def statement(self) -> Select:
        return select(EpisodeModel).filter().options(selectinload(EpisodeModel.season))

    async def process(self, *args, **kwargs) -> Page[ListEpisodesResponse]:
        return await paginate(
            self.session,
            self.statement,
        )
