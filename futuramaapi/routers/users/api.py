from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelExistsError, UnauthorizedResponse

from .dependencies import from_signature, from_token
from .schemas import User, UserAlreadyActivatedError, UserCreateRequest, UserUpdateRequest

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    name="user",
)
async def create_user(
    data: UserCreateRequest,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    """Create User.

    The user add endpoint is an API function allowing the creation of new user accounts.
    It receives user details via HTTP requests, validates the information,
    and stores it in the system's database.
    This endpoint is essential for user registration and onboarding.

    Please note that currently endpoint is not protected.
    However, if there are a lot of spam requests, the endpoint will be blocked or limited.
    """
    try:
        return await User.create(session, data)
    except ModelExistsError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User already exists.",
        ) from None


@router.get(
    "/me",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    name="user_me",
)
async def get_me(
    user: Annotated[User, Depends(from_token)],
) -> User:
    """Get user details.

    Retrieve authenticated user profile information, including username, email, and account details.
    Personalize user experiences within the application using the JSON response containing user-specific data.
    """
    return user


@router.get(
    "/activate",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        }
    },
    status_code=status.HTTP_200_OK,
    name="activate_user",
)
async def activate_user(
    user: User = Depends(from_signature),  # noqa: B008
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> None:
    """Activate user."""
    try:
        await user.activate(session)
    except UserAlreadyActivatedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User already activated.",
        ) from None


@router.put(
    "",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    name="update_user",
)
async def update_user(
    user: Annotated[User, Depends(from_token)],
    data: UserUpdateRequest,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> User:
    """Update user details.

    This endpoint is crucial for users to manage and maintain accurate profile information,
    often including authentication and authorization checks for security.
    """
    await user.update(session, data)
    return user


@router.post(
    "/confirmations/resend",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    status_code=status.HTTP_200_OK,
    name="resend_user_confirmation",
)
async def resend_user_confirmation(
    user: Annotated[User, Depends(from_token)],
) -> None:
    """Resend user confirmation.

    If the confirmation message is not delivered or got lost, user can request another message.
    """
    try:
        await user.send_confirmation_email()
    except UserAlreadyActivatedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User already activated.",
        ) from None
