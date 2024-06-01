from pathlib import Path
from typing import TYPE_CHECKING

from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

if TYPE_CHECKING:
    from fastapi import Request
    from starlette.datastructures import URL

TEMPLATES_PATH: Path = Path("templates")


@pass_context
def relative_path_for(context: dict, name: str, /, **path_params) -> str:
    request: "Request" = context["request"]
    http_url: "URL" = request.url_for(name, **path_params)
    return http_url.path


def _build_templates(templates_dir: Path) -> Jinja2Templates:
    _templates: Jinja2Templates = Jinja2Templates(directory=str(templates_dir))
    _templates.env.globals["relative_path_for"] = relative_path_for
    return _templates


templates: Jinja2Templates = _build_templates(TEMPLATES_PATH)
