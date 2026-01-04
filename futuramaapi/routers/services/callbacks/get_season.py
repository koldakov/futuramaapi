from fastapi import BackgroundTasks

from futuramaapi.routers.services import BaseService
from futuramaapi.tasks.callbacks.get_season import GetSeasonCallbackTaskService

from ._base import (
    CallbackRequest,
    CallbackResponse,
)


class GetSeasonCallbackService(BaseService):
    request_data: CallbackRequest
    id: int

    async def __call__(self, background_tasks: BackgroundTasks, *args, **kwargs) -> CallbackResponse:
        response: CallbackResponse = CallbackResponse()
        service: GetSeasonCallbackTaskService = GetSeasonCallbackTaskService(
            id=self.id,
            delay=response.delay,
            callback_url=self.request_data.callback_url,
        )
        background_tasks.add_task(service)
        return response
