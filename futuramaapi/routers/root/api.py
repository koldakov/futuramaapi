from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session

from .schemas import About, Root

router = APIRouter()


@router.get(
    "/health",
    tags=[
        "health",
    ],
    include_in_schema=False,
)
def health() -> Response:
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/favicon.ico",
    include_in_schema=False,
)
async def favicon():
    return FileResponse("favicon.ico")


@router.get(
    "/swagger",
    include_in_schema=False,
    name="swagger",
)
async def get_swagger():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Documentation | Futurama API",
        swagger_favicon_url="/favicon.ico",
    )


@router.get(
    "/docs",
    include_in_schema=False,
    name="redoc_html",
)
async def get_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Documentation | Futurama API",
        redoc_favicon_url="/favicon.ico",
    )


@router.get(
    "/",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
    name="root",
)
async def get_root(
    request: Request,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Response:
    obj: Root = await Root.from_request(session, request)
    return obj.get_response(request)


@router.get(
    "/about",
    include_in_schema=False,
    name="about",
)
async def about(
    request: Request,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Response:
    obj: About = await About.from_request(session, request)
    return obj.get_response(request)
