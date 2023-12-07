from fastapi import APIRouter, Request, status
from fastapi.responses import FileResponse, Response

from app.templates import templates

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
async def get_root(request: Request) -> Response:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@router.get(
    "/favicon.ico",
    include_in_schema=False,
)
async def favicon():
    return FileResponse("favicon.ico")
