from fastapi import APIRouter, Depends, Request, status
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.root import process_get_root
from app.templates import gnu_translations

router = APIRouter()


@router.get(
    "/health",
    tags=["health_check"],
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
async def get_health() -> Response:
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
    name="root",
)
async def get_root(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    return await process_get_root(request, session)


@router.get(
    "/favicon.ico",
    include_in_schema=False,
)
async def favicon() -> FileResponse:
    return FileResponse("favicon.ico")


@router.get(
    "/docs",
    include_in_schema=False,
    name="redoc_html",
)
async def get_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f'{gnu_translations.gettext("FB00003")} | {gnu_translations.gettext("FB00001")}',
        redoc_favicon_url="/favicon.ico",
    )
