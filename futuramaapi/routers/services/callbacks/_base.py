from random import randint

from pydantic import Field, HttpUrl

from futuramaapi.helpers.pydantic import BaseModel

MIN_DELAY: int = 5
MAX_DELAY: int = 10


class DoesNotExist(BaseModel):
    id: int = Field(
        description="Requested Object ID.",
    )
    detail: str = Field(
        default="Not found",
        examples=[
            "Not found",
        ],
    )


class CallbackRequest(BaseModel):
    callback_url: HttpUrl


class CallbackResponse(BaseModel):
    @staticmethod
    def _generate_random_delay() -> int:
        return randint(MIN_DELAY, MAX_DELAY)  # noqa: S311

    delay: int = Field(
        default_factory=_generate_random_delay,
        ge=MIN_DELAY,
        le=MAX_DELAY,
        description="Delay after which the callback will be sent.",
    )
