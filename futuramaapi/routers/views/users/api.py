from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from futuramaapi.routers.exceptions import UnauthorizedResponse
from futuramaapi.routers.services.users.activate_signature_user import ActivateSignatureUserService

router: APIRouter = APIRouter(
    prefix="/users",
)


@router.get(
    "/activate",
    include_in_schema=False,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        }
    },
    status_code=status.HTTP_200_OK,
    name="activate_signature_user",
)
async def activate_signature_user(
    request: Request,
    sig: str,
) -> RedirectResponse:
    service: ActivateSignatureUserService = ActivateSignatureUserService(
        signature=sig,
        context={
            "request": request,
        },
    )
    return await service()
