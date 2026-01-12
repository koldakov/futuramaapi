from typing import Annotated

from fastapi import APIRouter, Depends, status

from futuramaapi.routers.exceptions import UnauthorizedResponse
from futuramaapi.routers.rest.users.schemas import User

from .dependencies import from_form_data, refresh_token
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
    response_model=UserToken,
    name="user_token_auth",
)
async def token_auth_user(
    user: Annotated[User, Depends(from_form_data)],
) -> UserToken:
    """Authenticate user.

    JSON Web Token (JWT) authentication is a popular method for securing web applications and APIs.
    It enables the exchange of digitally signed tokens between a client (user) and a server,
    to authenticate and authorize users.

    Use a token in a response to get secured stored data of your user.
    """
    return UserToken.from_user(user)


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
