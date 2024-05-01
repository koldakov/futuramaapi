import logging

from starlette import status
from starlette.datastructures import URL
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.types import Scope

from futuramaapi.core import settings

logger = logging.getLogger(__name__)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    https_port: int = 443
    http_port: int = 80

    def is_secure(self, headers: dict):
        try:
            host: str = headers["host"]
        except KeyError:
            logger.info("Host not found in headers")
            return False
        try:
            proto: str = headers["x-forwarded-proto"]
        except KeyError:
            logger.info("x-forwarded-proto not found in headers")
            return False
        try:
            port: str = headers["x-forwarded-port"]
        except KeyError:
            logger.info("x-forwarded-port not found in headers")
            return False

        if host == settings.trusted_host and proto in ("https", "wss") and int(port) == self.https_port:
            return True
        return False

    def _fix_url(self, scope: Scope, /):
        url = URL(scope=scope)
        redirect_scheme = {"http": "https", "ws": "wss"}[url.scheme]
        netloc = url.hostname if url.port in (self.http_port, self.https_port) else url.netloc
        return url.replace(scheme=redirect_scheme, netloc=netloc)

    @staticmethod
    def headers_to_dict(headers: list, /) -> dict:
        return {h[0].decode(): h[1].decode() for h in headers}

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        headers: dict = self.headers_to_dict(request.scope["headers"])
        if self.is_secure(headers):
            return await call_next(request)

        url: URL = self._fix_url(request.scope)
        return RedirectResponse(
            url,
            status_code=status.HTTP_301_MOVED_PERMANENTLY,
            headers={h[0].decode(): h[1].decode() for h in request.scope["headers"]},
        )
