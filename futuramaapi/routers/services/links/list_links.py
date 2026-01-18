from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import Field
from sqlalchemy import Select, select

from futuramaapi.repositories.models import LinkModel
from futuramaapi.routers.services import BaseUserAuthenticatedService

from .get_link import GetLinkResponse


class ListLinksResponse(GetLinkResponse):
    pass


class ListLinksService(BaseUserAuthenticatedService[Page[ListLinksResponse]]):
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
    def _statement(self) -> Select[tuple[LinkModel]]:
        return select(LinkModel).order_by(LinkModel.created_at.desc())

    async def process(self, *args, **kwargs) -> Page[ListLinksResponse]:
        return await paginate(
            self.session,
            self._statement,
        )
