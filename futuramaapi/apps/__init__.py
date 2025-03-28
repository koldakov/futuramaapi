from fastapi import FastAPI

from .fastapi import futurama_api

app: FastAPI = futurama_api

__all__ = [
    "app",
]
