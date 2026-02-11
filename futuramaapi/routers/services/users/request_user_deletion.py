from futuramaapi.core import feature_flags
from futuramaapi.routers.services import BaseUserAuthenticatedService, UserDeletionDisabledError


class RequestUserDeletionService(BaseUserAuthenticatedService[None]):
    async def process(self, *args, **kwargs) -> None:
        if not feature_flags.user_deletion:
            raise UserDeletionDisabledError()

        raise NotImplementedError()
