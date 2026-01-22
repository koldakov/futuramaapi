from typing import Self

from fastapi import HTTPException, status
from pydantic import HttpUrl, model_validator

from futuramaapi.core import feature_flags, settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.mixins.pydantic import TemplateBodyMixin
from futuramaapi.routers.rest.tokens.schemas import DecodedUserToken
from futuramaapi.routers.services import BaseUserAuthenticatedService


class ConfirmationBody(BaseModel, TemplateBodyMixin):
    @property
    def signature(self) -> str:
        return DecodedUserToken(
            type="access",
            user={
                "id": self.user.id,
            },
        ).tokenize(self.expiration_time)

    @model_validator(mode="after")
    def build_confirmation_url(self) -> Self:
        self.url = HttpUrl.build(
            scheme=self.url.scheme,
            host=self.url.host,
            path="users/activate",
            query=f"sig={self.signature}",
        )
        return self


class ResendUserConfirmationService(BaseUserAuthenticatedService[None]):
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
            ConfirmationBody.model_validate(
                {
                    "user": {
                        "id": self.user.id,
                        "name": self.user.name,
                        "surname": self.user.surname,
                    },
                },
            ),
            "emails/confirmation.html",
        )
