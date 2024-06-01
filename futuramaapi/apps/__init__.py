from fastapi import FastAPI

from .app import futurama_api
from .hypercorn import run

app: FastAPI = futurama_api.app

__all__ = [
    "app",
    "run",
]
