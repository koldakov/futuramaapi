from fastapi.responses import RedirectResponse
from sqlalchemy import Result, Select, select
from sqlalchemy.exc import NoResultFound

from futuramaapi.repositories.models import LinkModel
from futuramaapi.routers.services import BaseSessionService, NotFoundError


class RedirectLinkService(BaseSessionService[RedirectResponse]):
    shortened: str

    @property
    def _statement(self) -> Select[tuple[LinkModel]]:
        return select(LinkModel).where(LinkModel.shortened == self.shortened)

    async def process(self, *args, **kwargs) -> RedirectResponse:
        result: Result[tuple[LinkModel]] = await self.session.execute(self._statement)
        try:
            link: LinkModel = result.scalars().one()
        except NoResultFound:
            raise NotFoundError("Link not found") from None

        link.counter += 1
        await self.session.commit()

        return RedirectResponse(link.url)
