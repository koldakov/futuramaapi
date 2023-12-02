import gettext

from fastapi.templating import Jinja2Templates

try:
    gnu_translations = gettext.translation(
        domain="messages",
        localedir="locale",
        languages=["en_US"],
    )
except FileNotFoundError:
    raise RuntimeError("Please compile messages first")


templates = Jinja2Templates(directory="templates", extensions=["jinja2.ext.i18n"])
templates.env.install_gettext_translations(gnu_translations)
