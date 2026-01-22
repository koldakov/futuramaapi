from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import UnauthorizedResponse

from .dependencies import from_signature
from .schemas import (
    User,
    UserAlreadyActivatedError,
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
