import mimetypes

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from app.configs import settings
from app.routers.characters import router as characters_router
from app.routers.episodes import router as episodes_router
from app.routers.root import router as root_router

mimetypes.add_type("image/webp", ".webp")

app = FastAPI(
    docs_url=None,
    redoc_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)

# API
app.include_router(
    characters_router,
    tags=["characters"],
    prefix="/api",
)
app.include_router(
    episodes_router,
    tags=["episodes"],
    prefix="/api",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

add_pagination(app)
