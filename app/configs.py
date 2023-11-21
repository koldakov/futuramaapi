from json import loads
from os import environ
from typing import Any, Dict, List

from pydantic import BaseModel


def parse(cast: Any, setting: str, separator: str) -> Any:
    if cast is str:
        return setting
    elif cast is bool:
        return _parse_bool(setting)
    elif cast in (list, List):
        return _parse_list(setting, separator)
    elif cast in (dict, Dict):
        return _parse_dict(setting)
    raise NotImplementedError(f'Cast is not implemented. cast="{cast}"') from None


def _parse_list(setting: str, separator: str) -> List:
    return [
        _setting for _setting in "".join(setting.split()).split(separator) if _setting
    ]


def _parse_dict(setting: str) -> Dict:
    return loads(setting)


def _parse_bool(setting: str) -> bool:
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


def _parse_int(setting: str) -> int:
    try:
        return int(setting)
    except ValueError:
        raise NotImplementedError(
            f'Can\'t cast variable to int. variable="{setting}"'
        ) from None


def get_env_var(
    var: str,
    cast: Any = str,
    separator: str = ",",
    required=True,
    default: Any = None,
) -> Any:
    try:
        setting = environ[var]
    except KeyError:
        if not required:
            return default
        raise RuntimeError(f'Missing environment variable. variable="{var}"') from None
    return parse(cast, setting, separator)


class Settings(BaseModel):
    allow_origins: List = get_env_var("ALLOW_ORIGINS", cast=List)


settings = Settings()
