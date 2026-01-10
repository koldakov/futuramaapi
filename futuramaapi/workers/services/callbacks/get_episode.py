from datetime import date, datetime
from typing import Literal

from pydantic import Field, computed_field
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import EpisodeModel

from ._base import (
    DoesNotExistCallbackResponse,
    GetItemCallbackTaskService,
)


class GetEpisodeCallbackResponse(BaseModel):
    class EpisodeItem(BaseModel):
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

    kind: Literal["Episode"] = Field(
        "Episode",
        alias="type",
        description="Requested Object type.",
    )
    item: EpisodeItem | DoesNotExistCallbackResponse


class GetEpisodeCallbackTaskService(GetItemCallbackTaskService):
    model_class = EpisodeModel
    response_class = GetEpisodeCallbackResponse

    @property
    def _statement(self) -> Select[tuple[EpisodeModel]]:
        return select(EpisodeModel).options(selectinload(EpisodeModel.season)).where(EpisodeModel.id == self.id)
