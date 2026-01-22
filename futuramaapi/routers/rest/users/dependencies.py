from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.mixins.pydantic import DecodedTokenError
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError
from futuramaapi.routers.rest.tokens.schemas import DecodedUserToken
from futuramaapi.routers.rest.users.schemas import User

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/tokens/users/auth")


async def _get_user_from_token(
    sig: str,
    session: AsyncSession,
    type_: Literal["access", "refresh"],
    /,
) -> User:
    try:
        decoded_token: DecodedUserToken = DecodedUserToken.decode(sig, allowed_type=type_)
    except DecodedTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    try:
        user: User = await User.get(session, decoded_token.user.id)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    return user


async def from_signature(
    sig: str,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    return await _get_user_from_token(sig, session, "access")
