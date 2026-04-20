from enum import StrEnum
from typing import Any

from futuramaapi.routers.services import BaseTemplateService


class UserSignupMessageType(StrEnum):
    signup_disabled = "signup_disabled"
    user_exists = "user_exists"
    signup_success = "signup_success"
    validation_error = "validation_error"


class GetUserSignupService(BaseTemplateService):
    template_name = "signup.html"

    message_type: UserSignupMessageType | None

    async def get_context(self, *args, **kwargs) -> dict[str, Any]:
        return {
            "message_type": self.message_type,
        }
