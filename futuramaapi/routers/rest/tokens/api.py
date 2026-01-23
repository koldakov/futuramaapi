from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from futuramaapi.routers.exceptions import UnauthorizedResponse
from futuramaapi.routers.services.tokens.get_auth_user_token import (
    GetAuthUserTokenResponse,
    GetAuthUserTokenService,
)

from .dependencies import refresh_token
from .schemas import UserToken

router: APIRouter = APIRouter(
    prefix="/tokens",
    tags=["tokens"],
)


@router.post(
    "/users/auth",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    response_model=GetAuthUserTokenResponse,
    name="get_user_auth_token",
)
async def get_user_auth_token(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
) -> GetAuthUserTokenResponse:
    """Authenticate user.

    JSON Web Token (JWT) authentication is a popular method for securing web applications and APIs.
    It enables the exchange of digitally signed tokens between a client (user) and a server,
    to authenticate and authorize users.

    Use a token in a response to get secured stored data of your user.
    """
    service: GetAuthUserTokenService = GetAuthUserTokenService(
        username=form_data.username,
        password=SecretStr(form_data.password),
    )
    return await service()


@router.post(
    "/users/refresh",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    response_model=UserToken,
    name="user_token_auth_refresh",
)
async def refresh_token_auth_user(
    token: Annotated[UserToken, Depends(refresh_token)],
) -> UserToken:
    """Refresh JWT.

    The Refresh JWT Token endpoint extends the lifespan of JSON Web Tokens (JWTs) without requiring user
    reauthentication. This API feature ensures uninterrupted access to secured resources.
    """
    return token
