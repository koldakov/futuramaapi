from fastapi import BackgroundTasks

from futuramaapi.routers.services import BaseService
from futuramaapi.tasks.callbacks.get_episode import get_episode_callback_task

from ._base import (
    CallbackRequest,
    CallbackResponse,
)


class GetEpisodeCallbackService(BaseService):
    request_data: CallbackRequest
    id: int

    async def __call__(self, background_tasks: BackgroundTasks, *args, **kwargs) -> CallbackResponse:
        response: CallbackResponse = CallbackResponse()
        await get_episode_callback_task(
            background_tasks,
            self.id,
            response.delay,
            self.request_data.callback_url,
        )
        return response
