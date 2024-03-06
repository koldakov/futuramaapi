import logging

from starlette import status
from starlette.datastructures import URL
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core import settings

logger = logging.getLogger(__name__)


class HTTPSRedirectMiddleware:
    https_port = 443
    http_port = 80
    proto_header = "x-forwarded-proto"
    port_header = "x-forwarded-port"

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    def is_secure(self, headers: dict):
        try:
            host: str = headers["host"]
        except KeyError:
            logger.info("Host not found in headers")
            return False
        try:
            proto: str = headers[self.proto_header]
        except KeyError:
            logger.info("x-forwarded-proto not found in headers")
            return False
        try:
            port: str = headers[self.port_header]
        except KeyError:
            logger.info("x-forwarded-port not found in headers")
            return False

        if host == settings.trusted_host and proto in ("https", "wss") and int(port) == self.https_port:
            return True
        return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        headers: dict = {h[0].decode().lower(): h[1].decode() for h in scope["headers"]}
        if not self.is_secure(headers):
            url = URL(scope=scope)
            redirect_scheme = {"http": "https", "ws": "wss"}[url.scheme]
            netloc = url.hostname if url.port in (self.http_port, self.https_port) else url.netloc
            url = url.replace(scheme=redirect_scheme, netloc=netloc)
            response = RedirectResponse(
                url,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            )
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)
