from fastapi import BackgroundTasks

from futuramaapi.routers.services import BaseService
from futuramaapi.tasks.callbacks.get_season import send_get_season_callback

from ._base import (
    CallbackRequest,
    CallbackResponse,
)


class GetSeasonCallbackService(BaseService):
    request_data: CallbackRequest
    id: int

    async def __call__(self, background_tasks: BackgroundTasks, *args, **kwargs) -> CallbackResponse:
        response: CallbackResponse = CallbackResponse()
        await send_get_season_callback(
            background_tasks,
            self.id,
            response.delay,
            self.request_data.callback_url,
        )
        return response
