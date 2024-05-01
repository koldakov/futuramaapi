from fastapi import FastAPI

from .builder import build_app

app = FastAPI()
build_app(app)
