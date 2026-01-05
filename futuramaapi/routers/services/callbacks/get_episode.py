from fastapi import BackgroundTasks

from futuramaapi.routers.services import BaseService
from futuramaapi.tasks.callbacks.get_episode import send_get_episode_callback

from ._base import (
    CallbackRequest,
    CallbackResponse,
)


class GetEpisodeCallbackService(BaseService):
    request_data: CallbackRequest
    id: int

    async def __call__(self, background_tasks: BackgroundTasks, *args, **kwargs) -> CallbackResponse:
        response: CallbackResponse = CallbackResponse()
        await send_get_episode_callback(
            background_tasks,
            self.id,
            response.delay,
            self.request_data.callback_url,
        )
        return response
