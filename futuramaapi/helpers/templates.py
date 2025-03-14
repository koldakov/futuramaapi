from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi.templating import Jinja2Templates as _Jinja2Templates
from jinja2 import Environment, pass_context
from starlette.datastructures import URL

if TYPE_CHECKING:
    from fastapi import Request

TEMPLATES_PATH: Path = Path("templates")


class Jinja2Templates(_Jinja2Templates):
    def _setup_env_defaults(self, env: Environment) -> None:
        @pass_context
        def url_for(
            context: dict[str, Any],
            name: str,
            /,
            **path_params: Any,
        ) -> URL:
            request: Request = context["request"]
            return request.url_for(name, **path_params)

        env.globals.setdefault("url_for", url_for)

        @pass_context
        def relative_path_for(
            context: dict[str, Any],
            name: str,
            /,
            **path_params: Any,
        ) -> URL:
            request: Request = context["request"]
            http_url: URL = request.url_for(name, **path_params)
            return http_url.replace(netloc="", scheme="")

        env.globals.setdefault("relative_path_for", relative_path_for)


templates: Jinja2Templates = Jinja2Templates(TEMPLATES_PATH)
