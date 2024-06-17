from typing import Annotated, Literal

from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import SecretStr
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.mixins.pydantic import DecodedTokenError
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError
from futuramaapi.routers.tokens.schemas import DecodedUserToken
from futuramaapi.routers.users.schemas import User, UserUpdateRequest

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


async def from_token(
    token: Annotated[str, Depends(_oauth2_scheme)],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    return await _get_user_from_token(token, session, "access")


async def from_signature(
    sig: str,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    return await _get_user_from_token(sig, session, "access")


async def from_form_signature(
    sig: Annotated[
        str,
        Form(),
    ],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    return await _get_user_from_token(sig, session, "access")


def password_from_form_data(
    password1: Annotated[
        SecretStr,
        Form(
            min_length=8,
            max_length=128,
        ),
    ],
    password2: Annotated[
        SecretStr,
        Form(
            min_length=8,
            max_length=128,
        ),
    ],
) -> UserUpdateRequest:
    if password1.get_secret_value() != password2.get_secret_value():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords mismatch") from None

    return UserUpdateRequest(password=password1.get_secret_value())
