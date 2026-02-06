from sqlalchemy import Select, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.repositories.models import EpisodeModel
from futuramaapi.routers.services import BaseSessionService, NotFoundError
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
            raise NotFoundError() from None

        return GetRandomEpisodeResponse.model_validate(result)
