from fastapi import FastAPI

from .app import futurama_api

app: FastAPI = futurama_api

__all__ = [
    "app",
]
