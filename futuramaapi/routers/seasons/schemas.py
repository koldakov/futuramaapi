from futuramaapi.mixins.pydantic import BaseModelGetMixin
from futuramaapi.pydantic import BaseModel
from futuramaapi.repositories.base import Base
from futuramaapi.repositories.models import SeasonModel
from futuramaapi.routers.episodes.schemas import EpisodeBase


class Season(BaseModel, BaseModelGetMixin):
    class Episode(EpisodeBase): ...

    id: int
    episodes: list[Episode]

    @staticmethod
    def get_model() -> type[Base]:
        return SeasonModel
