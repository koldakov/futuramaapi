from fastapi import BackgroundTasks
from pydantic import HttpUrl

from futuramaapi.workers.services.callbacks.get_season import GetSeasonCallbackTaskService


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
