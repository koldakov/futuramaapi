from datetime import datetime

from pydantic import EmailStr, Field, SecretStr

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.routers.services import BaseUserAuthenticatedService


class GetUserMeResponse(BaseModel):
    id: int
    created_at: datetime
    name: str = Field(
        min_length=1,
        max_length=64,
    )
    surname: str = Field(
        min_length=1,
        max_length=64,
    )
    middle_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
    )
    email: EmailStr
    username: str = Field(
        min_length=5,
        max_length=64,
    )
    password: SecretStr = Field(
        min_length=8,
        max_length=128,
    )
    is_subscribed: bool
    is_confirmed: bool


class GetUserMeService(BaseUserAuthenticatedService[GetUserMeResponse]):
    async def process(self, *args, **kwargs) -> GetUserMeResponse:
        return GetUserMeResponse.model_validate(self.user)
