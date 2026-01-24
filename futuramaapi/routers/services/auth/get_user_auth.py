from enum import StrEnum
from typing import Any

from futuramaapi.routers.services import BaseTemplateService


class UserAuthMessageType(StrEnum):
    password_changed = "password_changed"  # noqa: S105
    incorrect_login = "incorrect_login"


class GetUserAuthService(BaseTemplateService):
    template_name = "auth.html"

    message_type: UserAuthMessageType | None

    async def get_context(self, *args, **kwargs) -> dict[str, Any]:
        return {
            "message_type": self.message_type,
        }
