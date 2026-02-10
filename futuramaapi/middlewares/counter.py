from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from futuramaapi.db.models import RequestsCounterModel


def _get_url(request: Request, /) -> str:
    # Quick fix
    return request.url.__str__().split("?")[0][:64]


class APIRequestsCounter(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.url.path.startswith("/api"):
            await RequestsCounterModel.count_url(_get_url(request))

        return await call_next(request)
