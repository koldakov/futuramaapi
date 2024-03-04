from pathlib import Path
from typing import Any
from urllib.parse import ParseResult, urlparse

from pydantic import EmailStr, Field, PostgresDsn
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


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


settings = Settings()


class FeatureFlags(BaseSettings):
    activate_users: bool = False
    enable_https_redirect: bool = False


feature_flags = FeatureFlags()
