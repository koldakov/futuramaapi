from typing import Any

from futuramaapi.routers.services import BaseTemplateService


class GetAboutService(BaseTemplateService):
    template_name = "about.html"

    async def get_context(self, *args, **kwargs) -> dict[str, Any]:
        return {}
