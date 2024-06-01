from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get(
    "/api/graphql",
    include_in_schema=False,
)
async def old_graphql():
    return RedirectResponse("/graphql")
