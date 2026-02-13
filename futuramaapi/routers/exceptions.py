from pydantic import Field

from futuramaapi.helpers.pydantic import BaseModel


class NotFoundResponse(BaseModel):
    detail: str = Field("Not Found")


class UnauthorizedResponse(BaseModel):
    detail: str = Field("Unauthorized")
