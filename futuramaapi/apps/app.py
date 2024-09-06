import mimetypes
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Self

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from starlette.applications import Starlette
from starlette.routing import BaseRoute
from starlette.types import Lifespan

from futuramaapi.__version__ import __version__
from futuramaapi.core import feature_flags, settings
from futuramaapi.middlewares.cors import CORSMiddleware
from futuramaapi.middlewares.secure import HTTPSRedirectMiddleware
from futuramaapi.repositories.session import session_manager
from futuramaapi.utils._compat import metadata

if TYPE_CHECKING:
    from pydantic import HttpUrl

mimetypes.add_type("image/webp", ".webp")


class BaseAPI(ABC):
    version: str = __version__

    def __init__(
        self,
        routers: list[APIRouter],
        *,
        lifespan: Lifespan[Self] | None,
    ) -> None:
        self._init_sentry()

        self.routers: list[APIRouter] = routers
        self.app: Starlette = self.get_app(lifespan)

        self.build()

    @staticmethod
    def _init_sentry() -> None:
        if feature_flags.enable_sentry is False or settings.sentry.dsn is None:
            return None

        sentry_sdk.init(
            dsn=settings.sentry.dsn,
            environment=settings.sentry.environment,
            traces_sample_rate=settings.sentry.traces_sample_rate,
            profiles_sample_rate=settings.sentry.profiles_sample_rate,
        )

    @property
    def description(self):
        summary: str = metadata["summary"]
        project_url: HttpUrl = settings.build_url(is_static=False)
        return f"{summary} [Go back home]({project_url})."

    @abstractmethod
    def get_app(
        self,
        lifespan: Lifespan[Self] | None,
        /,
    ) -> Starlette: ...

    @abstractmethod
    def build(self) -> None: ...


class FuturamaAPI(BaseAPI):
    def get_app(
        self,
        lifespan: Lifespan[Self] | None,
        /,
    ) -> Starlette:
        return FastAPI(
            docs_url=None,
            redoc_url=None,
            lifespan=lifespan,
            version=self.version,
            description=self.description,
        )

    def _add_middlewares(self) -> None:
        if feature_flags.enable_https_redirect:
            self.app.add_middleware(HTTPSRedirectMiddleware)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _add_routers(self) -> None:
        for router in self.routers:
            self.app.include_router(router)

    def _add_static(self) -> None:
        self.app.mount(
            "/static",
            StaticFiles(directory="static"),
            name="static",
        )

    def build(self) -> None:
        self._add_middlewares()
        self._add_routers()
        self._add_static()

        add_pagination(self.app)

    @property
    def urls(self) -> list[BaseRoute]:
        return self.app.routes


@asynccontextmanager
async def _lifespan(_: FastAPI):
    yield
    if session_manager.engine is not None:
        await session_manager.close()


def _get_routers() -> list[APIRouter]:
    from futuramaapi.routers import api_router, graphql_router, root_router

    return [
        api_router,
        graphql_router,
        root_router,
    ]


futurama_api: FuturamaAPI = FuturamaAPI(
    _get_routers(),
    lifespan=_lifespan,
)
