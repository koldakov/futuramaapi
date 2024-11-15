import mimetypes
from contextlib import asynccontextmanager
from typing import Literal, Self

from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from starlette.applications import Starlette
from starlette.routing import BaseRoute
from starlette.types import Lifespan

from futuramaapi.core import feature_flags, settings
from futuramaapi.middlewares.cors import CORSMiddleware
from futuramaapi.middlewares.secure import HTTPSRedirectMiddleware
from futuramaapi.repositories.session import session_manager

from ._base import BaseAPI

mimetypes.add_type("image/webp", ".webp")


BOTS_FORBIDDEN_URLS: tuple[str, ...] = (
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


def _is_route_public(
    url: BaseRoute,
    /,
    *,
    allowed_methods: list[Literal["GET", "POST", "HEAD", "PUT"]] | None = None,
) -> bool:
    if url.path.startswith(BOTS_FORBIDDEN_URLS):
        return False

    if allowed_methods is None:
        allowed_methods = ["GET"]

    if not hasattr(url, "methods"):
        return True

    if not any(x in allowed_methods for x in url.methods):
        return False

    return True


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

    @property
    def public_urls(self) -> list[BaseRoute]:
        urls: list[BaseRoute] = []
        for route in self.app.routes:
            if _is_route_public(route) and route.path not in [u.path for u in urls]:
                urls.append(route)

        return urls


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
