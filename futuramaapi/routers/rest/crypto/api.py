from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError, NotFoundResponse

from .schemas import (
    SecretMessage,
    SecretMessageCreateRequest,
    SecretMessageCreateResponse,
)

router = APIRouter(
    prefix="/crypto",
    tags=["crypto"],
)


@router.post(
    "/secret_message",
    status_code=status.HTTP_201_CREATED,
    response_model=SecretMessageCreateResponse,
    name="create_secret_message",
)
async def create_secret_message(
    data: SecretMessageCreateRequest,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> SecretMessageCreateResponse:
    """Create Secret message."""
    message: SecretMessage = await SecretMessage.create(
        session,
        data,
        extra_fields={
            "ip_address": "",
        },
    )
    return SecretMessageCreateResponse(**message.model_dump())


@router.get(
    "/secret_message/{url}",
    status_code=status.HTTP_200_OK,
    response_model=SecretMessage,
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
) -> SecretMessage:
    """Get Secret message.

    Message will be shown only once. No excuses.
    After it's shown we delete the message itself and fill the message with random data,
    so it can't be decrypted or hacked or whatever. It's absolutely safe.

    If someone sent you a link, you follow the link, and you see ``visitCounter`` more than 1 - bad news.
    The URL has 128 length, which means there are 36 in power of 128 possibilities, it's more than stars in the
    universe, no chances anyone can ever accidentally access URL that was provided for you.

    One more time: If a person wants to send you a hidden message that is only for you, you follow the link, and
    it shows you some random data and ``visitCounter`` more than 1 it means someone already read the message,
    be aware!

    From our side we store the message in encrypted way, I won't be saying we can't read the message, BUT
    we respect privacy and don't reveal any private date, moreover after 1st successful shown the secret message
    we change the secret message with some random data, so no one, absolutely no one can recover/hack/whatever
    your secret data.
    """
    try:
        return await SecretMessage.get_once(session, request, url)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        ) from None
