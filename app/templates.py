import gettext

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from starlette.datastructures import URL

try:
    gnu_translations = gettext.translation(
        domain="messages",
        localedir="locale",
        languages=["en_US"],
    )
except FileNotFoundError:
    raise RuntimeError("Please compile messages first")


@pass_context
def relative_path_for(context: dict, name: str, /, **path_params) -> str:
    request: Request = context["request"]
    http_url: URL = request.url_for(name, **path_params)
    return http_url.path


templates = Jinja2Templates(directory="templates", extensions=["jinja2.ext.i18n"])
templates.env.globals["relative_path_for"] = relative_path_for
templates.env.install_gettext_translations(gnu_translations)
