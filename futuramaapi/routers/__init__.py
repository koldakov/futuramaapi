from fastapi import APIRouter

from ._redirects import router as redirect_router
from .callbacks import router as callbacks_router
from .characters import router as characters_router
from .episodes import router as episodes_router
from .graphql import router as graphql_router
from .notifications import router as notification_router
from .root import router as root_router
from .seasons import router as seasons_router
from .tokens import router as tokens_router
from .users import router as users_router

__all__ = [
    "api_router",
    "graphql_router",
    "redirect_router",
    "root_router",
]

api_router = APIRouter(prefix="/api")

api_router.include_router(callbacks_router)
api_router.include_router(characters_router)
api_router.include_router(episodes_router)
api_router.include_router(notification_router)
api_router.include_router(seasons_router)
api_router.include_router(tokens_router)
api_router.include_router(users_router)
