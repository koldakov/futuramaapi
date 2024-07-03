from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError, NotFoundResponse

from .schemas import (
    HiddenSecretMessage,
    SecretMessage,
    SecretMessageCreateRequest,
)

router = APIRouter(
    prefix="/crypto",
    tags=["crypto"],
)


@router.post(
    "/secret_message",
    status_code=status.HTTP_201_CREATED,
    response_model=SecretMessage,
    name="create_secret_message",
)
async def create_secret_message(
    data: SecretMessageCreateRequest,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> SecretMessage:
    """Create Secret message."""
    return await SecretMessage.create(
        session,
        data,
        extra_fields={
            "ip_address": "",
        },
    )


@router.get(
    "/secret_message/{url}",
    status_code=status.HTTP_200_OK,
    response_model=SecretMessage | HiddenSecretMessage,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundResponse,
        },
    },
    name="get_secret_message",
)
async def get_secret_message(
    url: str,
    request: Request,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> SecretMessage | HiddenSecretMessage:
    """Get Secret message."""
    try:
        return await SecretMessage.get_once(session, request, url)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        ) from None
