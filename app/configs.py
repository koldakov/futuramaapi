from pathlib import Path
from urllib.parse import ParseResult, urlparse

from json import loads
from json.decoder import JSONDecodeError
from os import environ
from typing import Dict, List, Type, TypedDict, Unpack

from pydantic import BaseModel


class _ExtraSettingArg(TypedDict):
    async_: bool
    db_url: bool


def parse[T](
    cast: Type[T],
    setting: str,
    separator: str,
    /,
    **extra: Unpack[_ExtraSettingArg],
) -> T:
    if cast is str:
        return _parse_str(setting, **extra)
    elif cast is bool:
        return _parse_bool(setting)
    elif cast in (list, List):
        return _parse_list(setting, separator)
    elif cast in (dict, Dict):
        return _parse_dict(setting)
    raise NotImplementedError(f'Cast is not implemented. cast="{cast}"') from None


def _parse_str(setting: str, /, **extra: Unpack[_ExtraSettingArg]):
    try:
        is_db = extra["db_url"]
    except KeyError:
        return setting
    if is_db:
        return _fix_db_url(setting, **extra)
    return setting


def _fix_db_url(url: str, /, **extra: Unpack[_ExtraSettingArg]):
    db_url = urlparse(url)
    try:
        async_ = extra["async_"] or False
    except KeyError:
        async_ = False
    if db_url.scheme.split("+")[0] in ["postgres", "postgresql"]:
        return _fix_postgres_url(db_url, is_async=async_)
    raise NotImplementedError() from None


def _fix_postgres_url(url: ParseResult, /, *, is_async: bool = False):
    if is_async:
        return url._replace(scheme="postgresql+asyncpg").geturl()
    return url._replace(scheme="postgresql").geturl()


def _parse_list(setting: str, separator: str, /) -> List:
    return [
        _setting for _setting in "".join(setting.split()).split(separator) if _setting
    ]


def _parse_dict(setting: str, /) -> Dict:
    try:
        return loads(setting)
    except JSONDecodeError as err:
        raise RuntimeError() from err


def _parse_bool(setting: str, /) -> bool:
    if setting.lower() in (
        "on",
        "true",
        "1",
        "ok",
        "y",
        "yes",
    ):
        return True
    return False


def _parse_int(setting: str, /) -> int:
    try:
        return int(setting)
    except ValueError:
        raise NotImplementedError(
            f'Can\'t cast variable to int. variable="{setting}"'
        ) from None


def get_env_var[T](
    var: str,
    /,
    *,
    cast: Type[T] = str,
    separator: str = ",",
    required=True,
    default: T = None,
    **extra: Unpack[_ExtraSettingArg],
) -> T:
    try:
        setting = environ[var]
    except KeyError:
        if not required:
            return default
        raise RuntimeError(f'Missing environment variable. variable="{var}"') from None
    return parse(cast, setting, separator, **extra)


class Settings(BaseModel):
    allow_origins: List = get_env_var("ALLOW_ORIGINS", cast=List)
    database_url: str = get_env_var("DATABASE_URL", cast=str, async_=True, db_url=True)
    project_root: Path = Path(__file__).parent.parent.resolve()
    static: Path = Path("static")
    trusted_host: str = get_env_var("TRUSTED_HOST", cast=str)
    secret_key: str = get_env_var("SECRET_KEY", cast=str)


settings = Settings()
