from fastapi.middleware.cors import CORSMiddleware as CORSMiddlewareBase


class CORSMiddleware(CORSMiddlewareBase):
    def is_allowed_origin(self, origin: str) -> bool:
        # Starlette restricts to have origin "*" with allow_credentials for ``fastapi.middleware.cors.CORSMiddleware``.
        # But for FuturamaAPI it's fine if anyone can access API.
        # Not a security issue at all. But if you have any suggestions you are free to create a task here:
        # https://github.com/koldakov/futuramaapi/issues.
        return True
