from fastapi import APIRouter

from .api import router as api_router
from .s import router as s_router

__all__ = [
    "router",
]

router: APIRouter = APIRouter(
    include_in_schema=False,
)
router.include_router(api_router)
router.include_router(s_router)
