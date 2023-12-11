from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.root import process_get_root

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
