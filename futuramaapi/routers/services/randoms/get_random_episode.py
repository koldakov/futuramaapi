from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.repositories.models import EpisodeModel
from futuramaapi.routers.services import BaseSessionService
from futuramaapi.routers.services.episodes.get_episode import GetEpisodeResponse


class GetRandomEpisodeResponse(GetEpisodeResponse):
    pass


class GetRandomEpisodeService(BaseSessionService[GetRandomEpisodeResponse]):
    @property
    def statement(self) -> Select[tuple[EpisodeModel]]:
        return select(EpisodeModel).options(selectinload(EpisodeModel.season)).order_by(func.random()).limit(1)

    async def process(self, *args, **kwargs) -> GetRandomEpisodeResponse:
        try:
            result: EpisodeModel = (await self.session.execute(self.statement)).scalars().one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

        return GetRandomEpisodeResponse.model_validate(result)
