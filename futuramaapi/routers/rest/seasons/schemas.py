from typing import ClassVar

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.mixins.pydantic import BaseModelDatabaseMixin
from futuramaapi.repositories.models import SeasonModel
from futuramaapi.routers.rest.episodes.schemas import EpisodeBase


class Season(BaseModel, BaseModelDatabaseMixin):
    model: ClassVar[type[SeasonModel]] = SeasonModel

    class Episode(EpisodeBase): ...

    id: int
    episodes: list[Episode]
