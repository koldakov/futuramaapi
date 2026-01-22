from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import UnauthorizedResponse

from .dependencies import from_form_signature, from_signature, password_from_form_data
from .schemas import (
    PasswordChange,
    User,
    UserAlreadyActivatedError,
    UserUpdateRequest,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
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
    name="activate_user",
)
async def activate_user(
    user: User = Depends(from_signature),  # noqa: B008
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> None:
    """Activate user."""
    try:
        await user.activate(session)
    except UserAlreadyActivatedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User already activated.",
        ) from None


@router.get(
    "/passwords/change",
    include_in_schema=False,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        }
    },
    status_code=status.HTTP_200_OK,
    name="change_user_password_form",
)
async def change_user_password_form(
    request: Request,
    sig: str,
    user: User = Depends(from_signature),  # noqa: B008
) -> Response:
    """Show password change form."""
    response: PasswordChange = PasswordChange(user=user, sig=sig)
    return await response.get_response(request)


@router.post(
    "/passwords/change",
    include_in_schema=False,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        }
    },
    status_code=status.HTTP_200_OK,
    name="change_user_password",
)
async def change_user_password(
    data: UserUpdateRequest = Depends(password_from_form_data),  # noqa: B008
    user: User = Depends(from_form_signature),  # noqa: B008
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> None:
    """Change user password."""
    await user.update(session, data, is_confirmed=True)
