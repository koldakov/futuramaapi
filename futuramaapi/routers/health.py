from fastapi import APIRouter, Response, status

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
