from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError
from futuramaapi.routers.users.schemas import User, UserPasswordError

from .schemas import DecodedTokenError, UserToken, UserTokenRefreshRequest

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/tokens/users/auth")


async def from_form_data(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    try:
        user: User = await User.auth(session, form_data.username, form_data.password)
    except (ModelNotFoundError, UserPasswordError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    return user


def refresh_token(
    token: Annotated[str, Depends(_oauth2_scheme)],
    data: UserTokenRefreshRequest,
) -> UserToken:
    token_: UserToken = UserToken(
        access_token=token,
        refresh_token=data.refresh_token,
    )

    try:
        token_.refresh()
    except DecodedTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    return token_
