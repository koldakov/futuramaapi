import mimetypes
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

import sentry_sdk
from fastapi.routing import APIRouter
from starlette.applications import Starlette
from starlette.types import Lifespan

from futuramaapi.__version__ import __version__
from futuramaapi.core import feature_flags, settings
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
