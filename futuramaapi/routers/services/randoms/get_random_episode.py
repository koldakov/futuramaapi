from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.repositories.models import EpisodeModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services import BaseService
from futuramaapi.routers.services.episodes.get_episode import GetEpisodeResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GetRandomEpisodeResponse(GetEpisodeResponse):
    pass


class GetRandomEpisodeService(BaseService):
    @property
    def statement(self) -> Select[tuple[EpisodeModel]]:
        return select(EpisodeModel).options(selectinload(EpisodeModel.season)).order_by(func.random()).limit(1)

    async def __call__(self, *args, **kwargs) -> GetRandomEpisodeResponse:
        session: AsyncSession
        async with session_manager.session() as session:
            try:
                result: EpisodeModel = (await session.execute(self.statement)).scalars().one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

        return GetRandomEpisodeResponse.model_validate(result)
