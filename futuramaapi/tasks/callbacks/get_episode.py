from typing import Literal

from pydantic import Field
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import EpisodeModel
from futuramaapi.routers.services.episodes.get_episode import GetEpisodeResponse

from ._base import (
    DoesNotExistCallbackResponse,
    GetItemCallbackTaskService,
)


class GetEpisodeCallbackResponse(BaseModel):
    class EpisodeItem(GetEpisodeResponse):
        pass

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
