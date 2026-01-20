from fastapi import APIRouter, Request, Response, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse

from futuramaapi.routers.services.about.get_about import GetAboutService
from futuramaapi.routers.services.auth.get_user_auth import GetUserAuthService
from futuramaapi.routers.services.changelog.get_changelog import GetChangelogService
from futuramaapi.routers.services.index.get_index import GetIndexService
from futuramaapi.routers.services.sitemaps.get_sitemap import GetSiteMapService

router: APIRouter = APIRouter()


@router.get(
    "/favicon.ico",
)
async def favicon() -> FileResponse:
    return FileResponse("favicon.ico")


@router.get(
    "/health",
)
def health() -> Response:
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/swagger",
    name="swagger",
)
async def get_swagger() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Swagger Playground | Futurama API",
        swagger_favicon_url="/favicon.ico",
    )


@router.get(
    "/docs",
    name="redoc_html",
)
async def get_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Documentation | Futurama API",
        redoc_favicon_url="/favicon.ico",
    )


@router.get(
    "/robots.txt",
)
async def robots() -> FileResponse:
    return FileResponse("robots.txt")


@router.get(
    "/sitemap.xml",
)
async def get_sitemap() -> Response:
    service: GetSiteMapService = GetSiteMapService()
    return await service()


@router.get(
    "/",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
    name="get_index",
)
async def get_index(
    request: Request,
) -> Response:
    service: GetIndexService = GetIndexService(
        context={
            "request": request,
        },
    )
    return await service()


@router.get(
    "/about",
    include_in_schema=False,
    name="about",
)
async def about(
    request: Request,
) -> Response:
    service: GetAboutService = GetAboutService(
        context={
            "request": request,
        },
    )
    return await service()


@router.get(
    "/changelog",
    include_in_schema=False,
    name="changelog",
)
async def get_changelog(
    request: Request,
):
    service: GetChangelogService = GetChangelogService(
        context={
            "request": request,
        },
    )
    return await service()


@router.get(
    "/auth",
    include_in_schema=False,
    name="user_auth",
)
async def user_auth(
    request: Request,
) -> Response:
    service: GetUserAuthService = GetUserAuthService(
        context={
            "request": request,
        },
    )
    return await service()
