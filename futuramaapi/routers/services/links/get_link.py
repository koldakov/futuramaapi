from datetime import datetime
from typing import ClassVar

from pydantic import Field, HttpUrl, computed_field
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import LinkModel
from futuramaapi.routers.services import BaseUserAuthenticatedService, NotFoundError


class GetLinkResponse(BaseModel):
    url: HttpUrl = Field(
        examples=[
            "https://example.com",
        ],
    )
    shortened: str = Field(
        examples=[
            "LWlWthH",
        ],
    )
    created_at: datetime
    counter: int

    path_prefix: ClassVar[str] = "s"

    @computed_field(  # type: ignore[misc]
        examples=[
            settings.build_url(path=f"{path_prefix}/LWlWthH", is_static=False).unicode_string(),
        ],
        return_type=str,
    )
    @property
    def shortened_url(self) -> str:
        return settings.build_url(path=f"{self.path_prefix}/{self.shortened}", is_static=False).unicode_string()


class GetLinkService(BaseUserAuthenticatedService[GetLinkResponse]):
    link_id: int

    @property
    def _statement(self) -> Select[tuple[LinkModel]]:
        return select(LinkModel).where(LinkModel.id == self.link_id)

    async def process(self, *args, **kwargs) -> GetLinkResponse:
        result: Result[tuple[LinkModel]] = await self.session.execute(self._statement)

        try:
            link: LinkModel = result.scalars().one()
        except NoResultFound:
            raise NotFoundError("Link not found") from None

        return GetLinkResponse.model_validate(link)
