from pydantic import Field
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.db.models import SeasonModel
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.routers.services._base import BaseSessionService, NotFoundError


class GetSeasonResponse(BaseModel):
    class Episode(BaseModel):
        id: int
        name: str
        broadcast_number: int = Field(alias="number")
        production_code: str = Field(
            examples=[
                "1ACV01",
            ],
        )

    id: int
    episodes: list[Episode]


class GetSeasonService(BaseSessionService[GetSeasonResponse]):
    pk: int

    @property
    def statement(self) -> Select:
        return select(SeasonModel).where(SeasonModel.id == self.pk).options(selectinload(SeasonModel.episodes))

    async def process(self, *args, **kwargs) -> GetSeasonResponse:
        try:
            season_model: SeasonModel = (await self.session.execute(self.statement)).scalars().one()
        except NoResultFound:
            raise NotFoundError("Season not found") from None

        return GetSeasonResponse.model_validate(season_model)
