from dramatiq.brokers.redis import RedisBroker
from dramatiq.cli import (
    CPUS,
    main,
    make_argument_parser,
)

from futuramaapi.core import settings

from ._config import broker


def run(
    *,
    verbose: int = 0,
    processes: int = settings.worker.processes,
    threads: int = settings.worker.threads,
    queues: list[str] = settings.worker.queues,
    _: RedisBroker = broker,
) -> None:
    if processes > CPUS:
        raise RuntimeError(f"Attempt to set more CPUS than available; processes={processes}, CPUS={CPUS}.")

    parser = make_argument_parser()

    command: list[str] = [
        "--processes",
        str(processes),
        "--threads",
        str(threads),
        __name__,
    ]

    # if settings.debug:
    #     verbose = max(1, verbose)
    #     if HAS_WATCHDOG:
    #         command += ["--watch", str(settings.project_root)]
    #         raise NotImplementedError()

    if queues:
        command += ["--queues", *queues]

    command += verbose * ["-v"]
    args = parser.parse_args(command)

    main(args)
