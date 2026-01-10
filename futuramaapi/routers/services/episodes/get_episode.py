from datetime import date, datetime

from fastapi import HTTPException, status
from pydantic import Field, computed_field
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import EpisodeModel
from futuramaapi.routers.services import BaseSessionService


class GetEpisodeResponse(BaseModel):
    id: int
    name: str
    broadcast_number: int = Field(
        alias="number",
    )
    production_code: str = Field(
        examples=[
            "1ACV01",
        ],
    )

    class Season(BaseModel):
        id: int

    air_date: date | None
    duration: int | None
    created_at: datetime
    season: Season

    @computed_field(  # type: ignore[misc]
        examples=[
            "S01E01",
        ],
        return_type=str,
    )
    @property
    def broadcast_code(self) -> str:
        return f"S{self.season.id:02d}E{self.broadcast_number:02d}"


class GetEpisodeService(BaseSessionService[GetEpisodeResponse]):
    pk: int

    @property
    def statement(self) -> Select:
        return select(EpisodeModel).where(EpisodeModel.id == self.pk).options(selectinload(EpisodeModel.season))

    async def process(self, *args, **kwargs) -> GetEpisodeResponse:
        try:
            season_model: EpisodeModel = (await self.session.execute(self.statement)).scalars().one()
        except NoResultFound:
            raise HTTPException(
                detail="Episode not found",
                status_code=status.HTTP_404_NOT_FOUND,
            ) from None

        return GetEpisodeResponse.model_validate(season_model)
