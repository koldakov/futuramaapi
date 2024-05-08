from fastapi import APIRouter

from .characters import router as characters_router
from .episodes import router as episodes_router
from .health import router as health_router
from .seasons import router as seasons_router

api_router = APIRouter(prefix="/api")

api_router.include_router(characters_router)
api_router.include_router(episodes_router)
api_router.include_router(seasons_router)

__all__ = [
    "api_router",
    "health_router",
]
