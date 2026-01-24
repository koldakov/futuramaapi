from typing import Annotated

from fastapi import APIRouter, Form, Query, Request, Response, status
from pydantic import SecretStr
from starlette.responses import RedirectResponse

from futuramaapi.routers.exceptions import UnauthorizedResponse
from futuramaapi.routers.services.passwords.change_signature_requested_user_password import (
    ChangeSignatureRequestedUserPasswordService,
)
from futuramaapi.routers.services.passwords.get_signature_user_password_change_form import (
    ChangeFormError,
    GetSignatureUserPasswordChangeFormService,
)

router = APIRouter(
    prefix="/passwords",
    tags=["passwords"],
)


@router.get(
    "/change",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        }
    },
    status_code=status.HTTP_200_OK,
    name="get_signature_user_password_change_form",
)
async def get_signature_user_password_change_form(
    request: Request,
    sig: Annotated[
        str,
        Query(),
    ],
    error_type: Annotated[
        ChangeFormError | None,
        Query(
            alias="errorType",
        ),
    ] = None,
) -> Response:
    """Show password change form."""
    service: GetSignatureUserPasswordChangeFormService = GetSignatureUserPasswordChangeFormService(
        signature=sig,
        error_type=error_type,
        context={
            "request": request,
        },
    )
    return await service()


@router.post(
    "/change",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        }
    },
    status_code=status.HTTP_200_OK,
    name="change_signature_requested_user_password",
)
async def change_signature_requested_user_password(
    password1: Annotated[
        SecretStr,
        Form(
            min_length=8,
            max_length=128,
        ),
    ],
    password2: Annotated[
        SecretStr,
        Form(
            min_length=8,
            max_length=128,
        ),
    ],
    sig: Annotated[
        str,
        Query(),
    ],
    request: Request,
) -> RedirectResponse:
    """Change user password."""
    service: ChangeSignatureRequestedUserPasswordService = ChangeSignatureRequestedUserPasswordService(
        password1=password1,
        password2=password2,
        signature=sig,
        context={
            "request": request,
        },
    )
    return await service()
