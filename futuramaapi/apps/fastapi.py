import mimetypes
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, ClassVar, Literal, NamedTuple, Self

import sentry_sdk
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from starlette.routing import Host, Mount, Route, WebSocketRoute

from futuramaapi.__version__ import __version__
from futuramaapi.core import feature_flags, settings
from futuramaapi.middlewares.cors import CORSMiddleware
from futuramaapi.middlewares.counter import APIRequestsCounter
from futuramaapi.middlewares.secure import HTTPSRedirectMiddleware
from futuramaapi.repositories.session import session_manager
from futuramaapi.utils import metadata

if TYPE_CHECKING:
    from pydantic import HttpUrl

mimetypes.add_type("image/webp", ".webp")


class _ExceptionValue(NamedTuple):
    status_code: int
    default_message: str


class FuturamaAPI(FastAPI):
    BOTS_FORBIDDEN_URLS: ClassVar[tuple[str, ...]] = (
        "/favicon.ico",
        "/openapi.json",
        "/robots.txt",
        "/sitemap.xml",
        "/static",
        "/health",
        "/logout",
        "/api/",
        "/s/",
    )

    def __init__(self, **kwargs: Any) -> None:
        self._setup_sentry()

        kwargs.setdefault("docs_url", None)
        kwargs.setdefault("redoc_url", None)
        kwargs.setdefault("lifespan", self._lifespan)
        kwargs.setdefault("version", __version__)
        kwargs.setdefault("description", self._description)
        super().__init__(**kwargs)

    @asynccontextmanager
    async def _lifespan(self, _: Self, /) -> AsyncGenerator[None, Any]:
        yield
        if session_manager.engine is not None:
            await session_manager.close()

    @staticmethod
    def _setup_sentry() -> None:
        if feature_flags.enable_sentry is False or settings.sentry.dsn is None:
            return None

        sentry_sdk.init(
            dsn=settings.sentry.dsn,
            environment=settings.sentry.environment,
            traces_sample_rate=settings.sentry.traces_sample_rate,
            profiles_sample_rate=settings.sentry.profiles_sample_rate,
        )

    def _setup_middlewares(self) -> None:
        if feature_flags.enable_https_redirect:
            self.add_middleware(HTTPSRedirectMiddleware)

        self.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        if feature_flags.count_api_requests:
            self.add_middleware(APIRequestsCounter)

    def _setup_routers(self) -> None:
        from futuramaapi.routers import api_router, graphql_router, views_router  # noqa: PLC0415

        for router in [api_router, graphql_router, views_router]:
            self.include_router(router)

    def _setup_static(self) -> None:
        self.mount(
            "/static",
            StaticFiles(directory="static"),
            name="static",
        )

    def _exception_handler(self, _: Request, exc) -> Response:
        from futuramaapi.routers.services import ServiceError, UnauthorizedError  # noqa: PLC0415

        exception_to_value: dict[type[ServiceError], _ExceptionValue] = {
            UnauthorizedError: _ExceptionValue(
                status_code=status.HTTP_401_UNAUTHORIZED,
                default_message="Unauthorized",
            ),
        }

        exc_value = exception_to_value[type(exc)]
        return JSONResponse(
            status_code=exc_value.status_code,
            content={
                "detail": str(exc) or exc_value.default_message,
            },
        )

    def _setup_exceptions(self) -> None:
        from futuramaapi.routers.services import ServiceError  # noqa: PLC0415

        self.add_exception_handler(ServiceError, self._exception_handler)

    def setup(self) -> None:
        super().setup()

        self._setup_middlewares()
        self._setup_routers()
        self._setup_static()
        self._setup_exceptions()

        add_pagination(self)

    @property
    def _description(self):
        summary: str = metadata["summary"]
        project_url: HttpUrl = settings.build_url(is_static=False)
        return f"{summary} [Go back home]({project_url})."

    def _is_route_public(
        self,
        url: Route | WebSocketRoute | Mount | Host,
        /,
        *,
        allowed_methods: list[Literal["GET", "POST", "HEAD", "PUT"]] | None = None,
    ) -> bool:
        if url.path.startswith(self.BOTS_FORBIDDEN_URLS):
            return False

        if allowed_methods is None:
            allowed_methods = ["GET"]

        if not hasattr(url, "methods"):
            return True

        if not any(x in allowed_methods for x in url.methods):
            return False

        return True

    @property
    def public_urls(self) -> list[Route | WebSocketRoute | Mount | Host]:
        urls: list[Route | WebSocketRoute | Mount | Host] = []
        route: Route | WebSocketRoute | Mount | Host
        for route in self.routes:
            if self._is_route_public(route) and route.path not in [u.path for u in urls]:
                urls.append(route)

        return urls


futurama_api: FuturamaAPI = FuturamaAPI()
