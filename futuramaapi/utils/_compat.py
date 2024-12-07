import tomllib
from importlib.metadata import metadata as _metadata
from typing import Any

__all__ = [
    "config",
    "metadata",
]


def _get_config() -> dict[str, Any]:
    with open("pyproject.toml", "rb") as f:
        return tomllib.load(f)


metadata = _metadata("futuramaapi")
config: dict[str, Any] = _get_config()
