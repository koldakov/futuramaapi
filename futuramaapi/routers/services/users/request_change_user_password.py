from typing import ClassVar, Self

from pydantic import EmailStr, HttpUrl, model_validator
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.core import feature_flags, settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.mixins.pydantic import TemplateBodyMixin
from futuramaapi.repositories.models import UserModel
from futuramaapi.routers.rest.tokens.schemas import DecodedUserToken
from futuramaapi.routers.services import BaseSessionService


class RequestChangeUserPasswordRequest(BaseModel):
    email: EmailStr


class PasswordResetBody(BaseModel, TemplateBodyMixin):
    expiration_time: ClassVar[int] = 15 * 60

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
            path="passwords/change",
            query=f"sig={self.signature}",
        )
        return self


class RequestChangeUserPasswordService(BaseSessionService[None]):
    request_data: RequestChangeUserPasswordRequest

    @property
    def _user_statement(self) -> Select[tuple[UserModel]]:
        return select(UserModel).where(UserModel.email == self.request_data.email)

    async def process(self, *args, **kwargs) -> None:
        if not feature_flags.activate_users:
            return

        result: Result[tuple[UserModel]] = await self.session.execute(self._user_statement)
        try:
            user_model: UserModel = result.scalars().one()
        except NoResultFound:
            return

        await settings.email.send(
            [user_model.email],
            "FuturamaAPI - Password Reset",
            PasswordResetBody.model_validate(
                {
                    "user": {
                        "id": user_model.id,
                        "name": user_model.name,
                        "surname": user_model.surname,
                    },
                }
            ),
            "emails/password_reset.html",
        )
