from datetime import datetime

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import Field
from sqlalchemy import Select, select

from futuramaapi.db.models import UserModel
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.routers.services import BaseSessionService


class ListUsersResponse(BaseModel):
    id: int
    is_confirmed: bool
    created_at: datetime
    username: str = Field(
        min_length=5,
        max_length=64,
    )
    name: str | None = Field(
        min_length=1,
        max_length=64,
        default=None,
    )
    surname: str | None = Field(
        min_length=1,
        max_length=64,
        default=None,
    )


class ListUsersService(BaseSessionService[Page[ListUsersResponse]]):
    offset: int = Field(
        default=0,
    )
    limit: int = Field(
        default=20,
    )
    query: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )

    @property
    def _statement(self) -> Select[tuple[UserModel]]:
        statement: Select[tuple[UserModel]] = select(UserModel)
        if self.query is not None:
            statement = statement.where(UserModel.username.icontains(self.query))

        statement = statement.order_by(UserModel.created_at.desc())
        return statement

    async def process(self, *args, **kwargs) -> Page[ListUsersResponse]:
        return await paginate(
            self.session,
            self._statement,
        )
