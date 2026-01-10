from fastapi import BackgroundTasks

from futuramaapi.routers.services import BaseService
from futuramaapi.tasks.callbacks.get_season import get_season_callback_task

from ._base import (
    CallbackRequest,
    CallbackResponse,
)


class GetSeasonCallbackService(BaseService):
    request_data: CallbackRequest
    id: int

    async def __call__(self, background_tasks: BackgroundTasks, *args, **kwargs) -> CallbackResponse:
        response: CallbackResponse = CallbackResponse()
        await get_season_callback_task(
            background_tasks,
            self.id,
            response.delay,
            self.request_data.callback_url,
        )
        return response
