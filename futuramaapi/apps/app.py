import mimetypes
from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from futuramaapi.core import feature_flags, settings
from futuramaapi.middlewares.cors import CORSMiddleware
from futuramaapi.middlewares.secure import HTTPSRedirectMiddleware
from futuramaapi.repositories.session import session_manager

mimetypes.add_type("image/webp", ".webp")


class FuturamaAPI:
    def __init__(
        self,
        routers: list[APIRouter],
        *,
        lifespan: Generator[Any, Any, None] | Any | None,
    ) -> None:
        self.routers: list[APIRouter] = routers
        self.app: FastAPI = FastAPI(
            docs_url=None,
            redoc_url=None,
            lifespan=lifespan,
        )

        self.build()

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
