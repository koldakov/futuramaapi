import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, ClassVar

import jwt
from pydantic import EmailStr, HttpUrl
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.core import feature_flags, settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import UserModel
from futuramaapi.routers.services import BaseSessionService


class RequestChangeUserPasswordRequest(BaseModel):
    email: EmailStr


class RequestChangeUserPasswordService(BaseSessionService[None]):
    request_data: RequestChangeUserPasswordRequest

    expiration_time: ClassVar[int] = 15 * 60

    @property
    def _user_statement(self) -> Select[tuple[UserModel]]:
        return select(UserModel).where(UserModel.email == self.request_data.email)

    def _get_signature(
        self,
        user: UserModel,
        /,
        *,
        algorithm: str = "HS256",
    ) -> str:
        return jwt.encode(
            {
                "exp": datetime.now(UTC) + timedelta(seconds=self.expiration_time),
                "nonce": uuid.uuid4().hex,
                "type": "access",
                "user": {
                    "id": user.id,
                },
            },
            settings.secret_key.get_secret_value(),
            algorithm=algorithm,
        )

    def _get_confirmation_url(self, user: UserModel, /) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme="https",
            host=settings.trusted_host,
            path="passwords/change",
            query=f"sig={self._get_signature(user)}",
        )
        return str(url)

    def _get_template_body(self, user: UserModel, /) -> dict[str, Any]:
        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
            },
            "url": self._get_confirmation_url(user),
        }

    async def process(self, *args, **kwargs) -> None:
        if not feature_flags.activate_users:
            return

        result: Result[tuple[UserModel]] = await self.session.execute(self._user_statement)
        try:
            user: UserModel = result.scalars().one()
        except NoResultFound:
            return

        await settings.email.send(
            [user.email],
            "FuturamaAPI - Password Reset",
            self._get_template_body(user),
            "emails/password_reset.html",
        )
