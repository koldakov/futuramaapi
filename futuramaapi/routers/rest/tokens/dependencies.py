from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .schemas import DecodedTokenError, UserToken, UserTokenRefreshRequest

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/tokens/users/auth")


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
