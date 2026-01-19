from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from futuramaapi.routers.services.links.redirect_link import RedirectLinkService

router: APIRouter = APIRouter(
    prefix="/s",
)


@router.get(
    "/{shortened}",
)
async def redirect_link(
    shortened: str,
) -> RedirectResponse:
    service: RedirectLinkService = RedirectLinkService(shortened=shortened)
    return await service()
