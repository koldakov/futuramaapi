from pydantic import Field

from futuramaapi.helpers.pydantic import BaseModel


class ModelNotFoundError(Exception): ...


class ModelExistsError(Exception): ...


class NotFoundResponse(BaseModel):
    detail: str = Field("Not Found")


class UnauthorizedResponse(BaseModel):
    detail: str = Field("Unauthorized")
