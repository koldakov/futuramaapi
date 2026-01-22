from fastapi import APIRouter

from .graphql import router as graphql_router
from .rest.callbacks import router as callbacks_router
from .rest.characters import router as characters_router
from .rest.crypto import router as crypto_router
from .rest.episodes import router as episodes_router
from .rest.favorites import router as favorites_router
from .rest.links import router as links_router
from .rest.notifications import router as notification_router
from .rest.randoms import router as randoms_router
from .rest.seasons import router as seasons_router
from .rest.tokens import router as tokens_router
from .rest.users import router as users_router
from .rest.users_new import router as users_new_router
from .views import router as views_router

__all__ = [
    "api_router",
    "graphql_router",
    "views_router",
]

api_router = APIRouter(prefix="/api")

api_router.include_router(callbacks_router)
api_router.include_router(randoms_router)
api_router.include_router(characters_router)
api_router.include_router(crypto_router)
api_router.include_router(episodes_router)
api_router.include_router(notification_router)
api_router.include_router(seasons_router)
api_router.include_router(tokens_router)
api_router.include_router(users_router)
api_router.include_router(users_new_router)
api_router.include_router(links_router)
api_router.include_router(favorites_router)
