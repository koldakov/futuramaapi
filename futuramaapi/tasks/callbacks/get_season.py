from typing import Literal

from fastapi import BackgroundTasks
from pydantic import Field, HttpUrl
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import SeasonModel
from futuramaapi.routers.services.seasons.get_season import GetSeasonResponse

from ._base import (
    DoesNotExistCallbackResponse,
    GetItemCallbackTaskService,
)


class GetSeasonCallbackResponse(BaseModel):
    class SeasonItem(GetSeasonResponse):
        pass

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


async def get_season_callback_task(
    background_tasks: BackgroundTasks,
    pk: int,
    delay: int,
    callback_url: HttpUrl,
) -> None:
    service: GetSeasonCallbackTaskService = GetSeasonCallbackTaskService(
        id=pk,
        delay=delay,
        callback_url=callback_url,
    )
    background_tasks.add_task(service)
