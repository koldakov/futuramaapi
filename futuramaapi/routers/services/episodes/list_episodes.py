from typing import TYPE_CHECKING

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from futuramaapi.repositories.models import EpisodeModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services._base import BaseService
from futuramaapi.routers.services.episodes.get_episode import GetEpisodeResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ListEpisodesResponse(GetEpisodeResponse):
    pass


class ListEpisodesService(BaseService):
    @property
    def statement(self) -> Select:
        return select(EpisodeModel).filter().options(selectinload(EpisodeModel.season))

    async def __call__(self, *args, **kwargs) -> Page[ListEpisodesResponse]:
        session: AsyncSession
        async with session_manager.session() as session:
            return await paginate(
                session,
                self.statement,
            )
