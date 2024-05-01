from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.mixins.pydantic import DecodedTokenError
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError
from futuramaapi.routers.tokens.schemas import DecodedUserToken
from futuramaapi.routers.users.schemas import DecodedUserSignature, User

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/tokens/users/auth")


async def from_token(
    token: Annotated[str, Depends(_oauth2_scheme)],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    try:
        decoded_token: DecodedUserToken = DecodedUserToken.decode(token, allowed_type="access")
    except DecodedTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    try:
        user: User = await User.get(session, decoded_token.id)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    return user


async def from_signature(
    sig: str,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    try:
        decoded_signature: DecodedUserSignature = DecodedUserSignature.decode(sig)
    except DecodedTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    try:
        user: User = await User.get(session, decoded_signature.id)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    return user
