from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.base import FilterStatementKwargs
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelExistsError, UnauthorizedResponse

from .dependencies import from_form_signature, from_signature, from_token, password_from_form_data
from .schemas import (
    Link,
    LinkCreateRequest,
    PasswordChange,
    User,
    UserAlreadyActivatedError,
    UserCreateRequest,
    UserPasswordChangeRequest,
    UserUpdateRequest,
)

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
    include_in_schema=False,
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already activated.",
        ) from None


@router.post(
    "/passwords/request-change",
    status_code=status.HTTP_200_OK,
    name="request_user_password_change",
)
async def request_user_password_change(
    data: UserPasswordChangeRequest,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> None:
    """Request password change."""
    await data.request_password_reset(session)


@router.get(
    "/passwords/change",
    include_in_schema=False,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        }
    },
    status_code=status.HTTP_200_OK,
    name="change_user_password_form",
)
async def change_user_password_form(
    request: Request,
    sig: str,
    user: User = Depends(from_signature),  # noqa: B008
) -> Response:
    """Show password change form."""
    response: PasswordChange = PasswordChange(user=user, sig=sig)
    return response.get_response(request)


@router.post(
    "/passwords/change",
    include_in_schema=False,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        }
    },
    status_code=status.HTTP_200_OK,
    name="change_user_password",
)
async def change_user_password(
    data: UserUpdateRequest = Depends(password_from_form_data),  # noqa: B008
    user: User = Depends(from_form_signature),  # noqa: B008
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> None:
    """Change user password."""
    await user.update(session, data, is_confirmed=True)


@router.post(
    "/links",
    name="generate_user_link",
)
async def create_user_link(
    data: LinkCreateRequest,
    user: Annotated[User, Depends(from_token)],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Link:
    """Generate shortened URL."""
    return await Link.create(
        session,
        data,
        extra_fields={
            "user_id": user.id,
        },
    )


@router.get(
    "/links",
    status_code=status.HTTP_200_OK,
    response_model=Page[Link],
    name="user_links",
)
async def get_user_links(
    user: Annotated[User, Depends(from_token)],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Page[Link]:
    """Retrieve user links."""
    filter_params: FilterStatementKwargs = FilterStatementKwargs(
        offset=0,
        limit=20,
        extra={
            "user": user,
        },
    )
    return await Link.paginate(session, filter_params=filter_params)
