import multiprocessing
from base64 import urlsafe_b64encode
from functools import cached_property
from pathlib import Path
from typing import Any, Literal, get_origin
from urllib.parse import urlparse

from cryptography.fernet import Fernet
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr, Field, HttpUrl, PostgresDsn, RedisDsn, SecretStr
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from redis.asyncio import ConnectionPool

from futuramaapi.helpers.templates import TEMPLATES_PATH


class EmailSettings(BaseSettings):
    default_from: EmailStr = Field(
        alias="EMAIL_FROM_DEFAULT",
    )
    host_user: str
    host: str
    api_key: SecretStr
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


class RedisSettings(BaseSettings):
    rediscloud_url: RedisDsn

    @cached_property
    def pool(self) -> ConnectionPool:
        return ConnectionPool.from_url(
            self.rediscloud_url.unicode_string(),
            decode_responses=True,
        )


redis_settings = RedisSettings()


class WorkerSettings(BaseSettings):
    redis_broker_url: RedisDsn = redis_settings.rediscloud_url
    processes: int = multiprocessing.cpu_count()
    threads: int = 8
    queues: list[str] = Field(
        default_factory=list,
    )

    model_config = SettingsConfigDict(
        env_prefix="worker_",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (_EnvSource(settings_cls),)


class SentrySettings(BaseSettings):
    dsn: HttpUrl | None = None
    traces_sample_rate: float = Field(
        default=1.0,
        ge=0,
        le=1,
    )
    profiles_sample_rate: float = Field(
        default=1.0,
        ge=0,
        le=1,
    )
    # Not the best practice to split on environments and currently the code is totally abstract from
    # any environment, but it's really nice to have sentry divided on different environments.
    environment: Literal["development", "staging", "production"] = "production"

    model_config = SettingsConfigDict(
        env_prefix="sentry_",
    )


sentry_settings = SentrySettings()


def _parse_list(value: str | None, /) -> list[str]:
    if value is None:
        return []

    return [str(x).strip() for x in value.split(",")]


def _fix_postgres_url(url: str, /, *, scheme: str = "postgresql+asyncpg") -> str:
    return urlparse(url)._replace(scheme=scheme).geturl()


class _EnvSource(EnvSettingsSource):
    def prepare_field_value(
        self,
        field_name: str,
        field: FieldInfo,
        value: Any,
        value_is_complex: bool,
    ) -> Any:
        if get_origin(field.annotation) is list:
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
    secret_key: SecretStr
    email: EmailSettings = email_settings
    redis: RedisSettings = redis_settings
    sentry: SentrySettings = sentry_settings
    g_tag: str | None = Field(
        default=None,
        description="Google analytics tag.",
    )

    pool_max_overflow: int = 10
    pool_size: int = 5
    pool_timeout: int = 30
    pool_recycle: int = -1

    worker: WorkerSettings = WorkerSettings()

    @cached_property
    def fernet(self) -> Fernet:
        return Fernet(urlsafe_b64encode(self.secret_key.get_secret_value().encode().ljust(32)[:32]))

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (_EnvSource(settings_cls),)

    @staticmethod
    def _clean_path(path: str | None, /) -> str:
        if path is None:
            path = ""

        return path[1:] if path.startswith("/") else path

    def build_url(
        self,
        *,
        path: str | None = None,
        is_static: bool = True,
    ) -> HttpUrl:
        path = self._clean_path(path)
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
    enable_sentry: bool = False
    count_api_requests: bool = True
    user_signup: bool = True
    user_deletion: bool = False


feature_flags = FeatureFlags()
