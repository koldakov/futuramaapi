from importlib.metadata import metadata as _metadata

__all__ = [
    "metadata",
]

metadata = _metadata("futuramaapi")
