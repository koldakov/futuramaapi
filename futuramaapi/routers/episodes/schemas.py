from datetime import date, datetime

from pydantic import Field, computed_field

from futuramaapi.mixins.pydantic import BaseModelGetMixin
from futuramaapi.pydantic import BaseModel
from futuramaapi.repositories.base import Base
from futuramaapi.repositories.models import EpisodeModel


class EpisodeBase(BaseModel, BaseModelGetMixin):
    id: int
    name: str
    broadcast_number: int = Field(alias="number")
    production_code: str = Field(
        examples=[
            "1ACV01",
        ],
    )

    @staticmethod
    def get_model() -> type[Base]:
        return EpisodeModel


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
