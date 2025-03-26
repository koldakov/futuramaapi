import sys

from .web_servers import run


def _run() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(_run())
