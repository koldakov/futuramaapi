from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from .core import feature_flags, settings
from .middlewares.secure import HTTPSRedirectMiddleware
from .routers import api_router, health_router


def build_middlewares(app: FastAPI, /) -> None:
    if feature_flags.enable_https_redirect:
        app.add_middleware(HTTPSRedirectMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def build_routers(app: FastAPI, /) -> None:
    app.include_router(api_router)
    app.include_router(health_router)


def build_app(app: FastAPI, /) -> None:
    build_middlewares(app)
    build_routers(app)

    add_pagination(app)
