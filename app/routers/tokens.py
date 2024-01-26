from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.auth import oauth2_scheme
from app.services.security import (
    AccessTokenData,
    OAuth2PasswordRequestJson,
    UnauthorizedResponse,
)
from app.services.tokens import (
    Token,
    process_refresh_token_auth_user,
    process_token_auth_user,
)

router = APIRouter(prefix="/tokens")


@router.post(
    "/users/auth",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    response_model=Token,
    name="user_token_auth",
)
async def token_auth_user(
    form_data: Annotated[OAuth2PasswordRequestJson, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    """Authenticate user.

    JSON Web Token (JWT) authentication is a popular method for securing web applications and APIs.
    It enables the exchange of digitally signed tokens between a client (user) and a server,
    to authenticate and authorize users.

    Use a token in a response to get secured stored data of your user.
    """
    return await process_token_auth_user(session, form_data)


@router.post(
    "/users/refresh",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    response_model=Token,
    name="user_token_auth_refresh",
)
async def refresh_token_auth_user(
    token: Annotated[AccessTokenData, Depends(oauth2_scheme)],
) -> Token:
    """Refresh JWT.

    The Refresh JWT Token endpoint extends the lifespan of JSON Web Tokens (JWTs) without requiring user
    reauthentication. This API feature ensures uninterrupted access to secured resources.
    """
    return await process_refresh_token_auth_user(token)
