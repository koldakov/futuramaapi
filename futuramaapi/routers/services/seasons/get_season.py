from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from pydantic import Field
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import SeasonModel
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.services._base import BaseService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


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


class GetSeasonService(BaseService):
    pk: int

    @property
    def statement(self) -> Select:
        return select(SeasonModel).where(SeasonModel.id == self.pk).options(selectinload(SeasonModel.episodes))

    async def __call__(self, *args, **kwargs) -> GetSeasonResponse:
        session: AsyncSession
        async with session_manager.session() as session:
            try:
                season_model: SeasonModel = (await session.execute(self.statement)).scalars().one()
            except NoResultFound:
                raise HTTPException(
                    detail="Season not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                ) from None

        return GetSeasonResponse.model_validate(season_model)
