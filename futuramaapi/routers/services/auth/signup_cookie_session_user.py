from asyncpg import UniqueViolationError
from fastapi import status
from fastapi.responses import RedirectResponse
from pydantic import EmailStr, Field, SecretStr, field_validator
from sqlalchemy import exc

from futuramaapi.core import feature_flags
from futuramaapi.db.models import UserModel
from futuramaapi.routers.services import BaseSessionService
from futuramaapi.routers.services.auth.get_user_signup import UserSignupMessageType


class SignupCookieSessionUserService(BaseSessionService[RedirectResponse]):
    name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z\s\-']+$",
    )
    surname: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z\s\-']+$",
    )
    email: EmailStr = Field(max_length=320)
    username: str = Field(
        min_length=5,
        max_length=64,
        pattern=r"^[A-Za-z][A-Za-z0-9_]{4,}$",
    )
    password: SecretStr = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: SecretStr, /) -> SecretStr:
        password: str = value.get_secret_value()
        has_letter = any(character.isalpha() for character in password)
        has_digit = any(character.isdigit() for character in password)
        if not has_letter or not has_digit:
            raise ValueError("Password must contain at least one letter and one digit")

        return value

    async def process(self, *args, **kwargs) -> RedirectResponse:
        if not feature_flags.user_signup:
            return RedirectResponse(
                url=f"/signup?messageType={UserSignupMessageType.signup_disabled}",
                status_code=status.HTTP_302_FOUND,
            )

        user: UserModel = UserModel(
            name=self.name,
            surname=self.surname,
            email=self.email,
            username=self.username,
            password=self.hasher.encode(self.password.get_secret_value()),
        )
        self.session.add(user)

        try:
            await self.session.commit()
        except exc.IntegrityError as err:
            if hasattr(err.orig, "sqlstate") and err.orig.sqlstate == UniqueViolationError.sqlstate:
                return RedirectResponse(
                    url=f"/signup?messageType={UserSignupMessageType.user_exists}",
                    status_code=status.HTTP_302_FOUND,
                )
            raise

        return RedirectResponse(
            url=f"/auth?messageType={UserSignupMessageType.signup_success}",
            status_code=status.HTTP_302_FOUND,
        )
