from pydantic import Field

from futuramaapi.helpers import BaseSchema


class NotFoundResponse(BaseSchema):
    detail: str = Field("Not Found")


class UnauthorizedResponse(BaseSchema):
    detail: str = Field("Unauthorized")
