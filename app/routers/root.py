from fastapi import APIRouter, status
from fastapi.responses import Response

router = APIRouter()


@router.get(
    "/health",
    tags=["health_check"],
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
async def get_health() -> Response:
    return Response(status_code=status.HTTP_200_OK)
