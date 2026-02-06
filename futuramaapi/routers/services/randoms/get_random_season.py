from sqlalchemy import Select, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.repositories.models import SeasonModel
from futuramaapi.routers.services import BaseSessionService, NotFoundError
from futuramaapi.routers.services.seasons.get_season import GetSeasonResponse


class GetRandomSeasonResponse(GetSeasonResponse):
    pass


class GetRandomSeasonService(BaseSessionService[GetRandomSeasonResponse]):
    @property
    def statement(self) -> Select[tuple[SeasonModel]]:
        return select(SeasonModel).options(selectinload(SeasonModel.episodes)).order_by(func.random()).limit(1)

    async def process(self, *args, **kwargs) -> GetRandomSeasonResponse:
        try:
            result: SeasonModel = (await self.session.execute(self.statement)).scalars().one()
        except NoResultFound:
            raise NotFoundError() from None

        return GetRandomSeasonResponse.model_validate(result)
