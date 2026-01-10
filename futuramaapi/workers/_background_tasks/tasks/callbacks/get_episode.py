from fastapi import BackgroundTasks
from pydantic import HttpUrl

from futuramaapi.workers.services.callbacks.get_episode import GetEpisodeCallbackTaskService


async def get_episode_callback_task(
    background_tasks: BackgroundTasks,
    pk: int,
    delay: int,
    callback_url: HttpUrl,
) -> None:
    service: GetEpisodeCallbackTaskService = GetEpisodeCallbackTaskService(
        id=pk,
        delay=delay,
        callback_url=callback_url,
    )
    background_tasks.add_task(service)
