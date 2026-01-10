from typing import Literal

from pydantic import Field
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import SeasonModel

from ._base import (
    DoesNotExistCallbackResponse,
    GetItemCallbackTaskService,
)


class GetSeasonCallbackResponse(BaseModel):
    class SeasonItem(BaseModel):
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

    kind: Literal["Season"] = Field(
        "Season",
        alias="type",
        description="Requested Object type.",
    )
    item: SeasonItem | DoesNotExistCallbackResponse


class GetSeasonCallbackTaskService(GetItemCallbackTaskService):
    model_class = SeasonModel
    response_class = GetSeasonCallbackResponse

    @property
    def _statement(self) -> Select[tuple[SeasonModel]]:
        return select(SeasonModel).options(selectinload(SeasonModel.episodes)).where(SeasonModel.id == self.id)
