import sys
from typing import TYPE_CHECKING

from hypercorn.__main__ import main

if TYPE_CHECKING:
    from collections.abc import Sequence


class Config:
    worker_class = "uvloop"


hypercorn_config: Config = Config()


def run(
    args: list[str] | None,
) -> int:
    argv: Sequence[str] = args if args is not None else sys.argv[1:]
    main(
        [
            "futuramaapi:app",
            "--config=python:futuramaapi.web_servers.hypercorn.hypercorn_config",
            *argv,
        ]
    )
    return 0
