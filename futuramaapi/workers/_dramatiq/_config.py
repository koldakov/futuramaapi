import dramatiq
from dramatiq.brokers.redis import RedisBroker as _RedisBroker
from dramatiq.middleware import AsyncIO, CurrentMessage
from pydantic import RedisDsn

from futuramaapi.core import settings


class RedisBroker(_RedisBroker):
    def __init__(
        self,
        *,
        url: RedisDsn = settings.worker.redis_broker_url,
        **parameters,
    ) -> None:
        super().__init__(
            url=str(url),
            **parameters,
        )

        self._post_init()

    def _post_init(self) -> None:
        self.add_middleware(AsyncIO())
        self.add_middleware(CurrentMessage())
        dramatiq.set_broker(self)


broker: RedisBroker = RedisBroker()
