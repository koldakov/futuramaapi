from typing import Any

from futuramaapi.routers.services import BaseTemplateService


class GetUserAuthService(BaseTemplateService):
    template_name = "auth.html"

    async def get_context(self, *args, **kwargs) -> dict[str, Any]:
        return {}
