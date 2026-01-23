import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, ClassVar

import jwt
from fastapi import HTTPException, status
from pydantic import HttpUrl

from futuramaapi.core import feature_flags, settings
from futuramaapi.routers.services import BaseUserAuthenticatedService


class ResendUserConfirmationService(BaseUserAuthenticatedService[None]):
    expiration_time: ClassVar[int] = 3 * 24 * 60 * 60

    def _get_signature(
        self,
        *,
        algorithm: str = "HS256",
    ) -> str:
        return jwt.encode(
            {
                "exp": datetime.now(UTC) + timedelta(seconds=self.expiration_time),
                "nonce": uuid.uuid4().hex,
                "type": "access",
                "user": {
                    "id": self.user.id,
                },
            },
            settings.secret_key.get_secret_value(),
            algorithm=algorithm,
        )

    def _get_confirmation_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme="https",
            host=settings.trusted_host,
            path="users/activate",
            query=f"sig={self._get_signature()}",
        )
        return str(url)

    def _get_template_body(self) -> dict[str, Any]:
        return {
            "user": {
                "id": self.user.id,
                "name": self.user.name,
                "surname": self.user.surname,
            },
            "url": self._get_confirmation_url(),
        }

    async def process(self, *args, **kwargs) -> None:
        if self.user.is_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already activated.",
            ) from None

        if not feature_flags.activate_users:
            return

        await settings.email.send(
            [self.user.email],
            "FuturamaAPI - Account Activation",
            self._get_template_body(),
            "emails/confirmation.html",
        )
