from pathlib import Path
from typing import Any
from urllib.parse import ParseResult, urlparse

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr, Field, HttpUrl, PostgresDsn
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from futuramaapi.helpers.templates import TEMPLATES_PATH


class EmailSettings(BaseSettings):
    default_from: EmailStr = Field(
        alias="EMAIL_FROM_DEFAULT",
    )
    host_user: str
    host: str
    api_key: str
    port: int = 587
    from_name: str = "FuturamaAPI"
    start_tls: bool = True
    ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True

    model_config = SettingsConfigDict(
        env_prefix="email_",
    )

    @property
    def fast_mail(self) -> FastMail:
        return FastMail(self.connection_config)

    @property
    def connection_config(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=self.host_user,
            MAIL_PASSWORD=self.api_key,
            MAIL_FROM=self.default_from,
            MAIL_PORT=self.port,
            MAIL_SERVER=self.host,
            MAIL_FROM_NAME=self.from_name,
            MAIL_STARTTLS=self.start_tls,
            MAIL_SSL_TLS=self.ssl_tls,
            USE_CREDENTIALS=self.use_credentials,
            VALIDATE_CERTS=self.validate_certs,
            TEMPLATE_FOLDER=settings.project_root / TEMPLATES_PATH,
        )

    @staticmethod
    def get_message_schema(
        subject: str,
        emails: list[EmailStr],
        template_body: BaseModel | dict,
    ) -> MessageSchema:
        body: dict = template_body
        if isinstance(template_body, BaseModel):
            body = template_body.model_dump()
        return MessageSchema(
            subject=subject,
            recipients=emails,
            template_body=body,
            subtype=MessageType.html,
        )

    async def send(
        self,
        emails: list[EmailStr],
        subject: str,
        template_body: BaseModel | dict,
        template_name: str,
        /,
    ):
        if feature_flags.send_emails is False:
            return

        await self.fast_mail.send_message(
            self.get_message_schema(
                subject,
                emails,
                template_body,
            ),
            template_name=template_name,
        )


email_settings = EmailSettings()


def _parse_list(value: str) -> list[str]:
    return [str(x).strip() for x in value.split(",")]


def _fix_postgres_url(url: str, /) -> str:
    db_url: ParseResult = urlparse(url)
    return db_url._replace(scheme="postgresql+asyncpg").geturl()


class _EnvSource(EnvSettingsSource):
    def prepare_field_value(
        self,
        field_name: str,
        field: FieldInfo,
        value: Any,
        value_is_complex: bool,
    ) -> Any:
        if field_name == "allow_origins":
            return _parse_list(value)
        if field_name == "database_url":
            return PostgresDsn(_fix_postgres_url(value))
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    allow_origins: list[str]
    database_url: PostgresDsn
    project_root: Path = Path(__file__).parent.parent.parent.resolve()
    static: Path = Path("static")
    trusted_host: str
    secret_key: str
    email: EmailSettings = email_settings

    @classmethod
    def settings_customise_sources(  # noqa: PLR0913
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (_EnvSource(settings_cls),)

    def build_url(
        self,
        *,
        path: str | None = None,
        is_static: bool = True,
    ) -> HttpUrl:
        path = path if path is not None else ""
        if is_static is True:
            path = f"{self.static}/{path}" if path else f"{self.static}"

        return HttpUrl.build(
            scheme="https",
            host=self.trusted_host,
            path=path,
        )


settings = Settings()


class FeatureFlags(BaseSettings):
    enable_https_redirect: bool = False
    send_emails: bool = True
    activate_users: bool = False


feature_flags = FeatureFlags()
