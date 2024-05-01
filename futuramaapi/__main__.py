import sys

from .apps import run


def _run() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(_run())
