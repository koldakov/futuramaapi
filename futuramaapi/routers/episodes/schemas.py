from datetime import date, datetime
from typing import ClassVar

from pydantic import Field, computed_field

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.mixins.pydantic import BaseModelDatabaseMixin
from futuramaapi.repositories.models import EpisodeModel


class EpisodeBase(BaseModel, BaseModelDatabaseMixin):
    model: ClassVar[type[EpisodeModel]] = EpisodeModel

    id: int
    name: str
    broadcast_number: int = Field(alias="number")
    production_code: str = Field(
        examples=[
            "1ACV01",
        ],
    )


class Episode(EpisodeBase):
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
