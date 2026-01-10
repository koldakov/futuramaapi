from fastapi import HTTPException, status
from pydantic import Field
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import SeasonModel
from futuramaapi.routers.services._base import BaseSessionService


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
            raise HTTPException(
                detail="Season not found",
                status_code=status.HTTP_404_NOT_FOUND,
            ) from None

        return GetSeasonResponse.model_validate(season_model)
