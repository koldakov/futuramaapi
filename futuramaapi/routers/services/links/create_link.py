from pydantic import HttpUrl

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import LinkModel
from futuramaapi.routers.services import BaseUserAuthenticatedService

from .get_link import GetLinkResponse


class CreateLinkRequest(BaseModel):
    url: HttpUrl


class CreateLinkResponse(GetLinkResponse):
    pass


class CreateLinkService(BaseUserAuthenticatedService):
    request_data: CreateLinkRequest

    def _get_link(self) -> LinkModel:
        return LinkModel(**self.request_data.to_dict(by_alias=False), user_id=self.user.id)

    async def process(self, *args, **kwargs) -> CreateLinkResponse:
        link_model: LinkModel = self._get_link()
        self.session.add(link_model)

        await self.session.commit()

        return CreateLinkResponse.model_validate(link_model)
