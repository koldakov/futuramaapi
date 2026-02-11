from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page

from futuramaapi.routers.exceptions import UnauthorizedResponse
from futuramaapi.routers.rest.users.dependencies import _oauth2_scheme
from futuramaapi.routers.services.users.create_user import (
    CreateUserRequest,
    CreateUserResponse,
    CreateUserService,
)
from futuramaapi.routers.services.users.get_user_me import (
    GetUserMeResponse,
    GetUserMeService,
)
from futuramaapi.routers.services.users.list_users import (
    ListUsersResponse,
    ListUsersService,
)
from futuramaapi.routers.services.users.request_change_user_password import (
    RequestChangeUserPasswordRequest,
    RequestChangeUserPasswordService,
)
from futuramaapi.routers.services.users.request_user_deletion import RequestUserDeletionService
from futuramaapi.routers.services.users.resend_user_confirmation import ResendUserConfirmationService
from futuramaapi.routers.services.users.update_user import (
    UpdateUserRequest,
    UpdateUserResponse,
    UpdateUserService,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
    responses={
        status.HTTP_201_CREATED: {
            "model": CreateUserResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User registration is currently disabled.",
        },
        status.HTTP_409_CONFLICT: {
            "description": "User already exists.",
        },
    },
    name="create_user",
)
async def create_user(
    data: CreateUserRequest,
) -> CreateUserResponse:
    """Create User.

    The user add endpoint is an API function allowing the creation of new user accounts.
    It receives user details via HTTP requests, validates the information,
    and stores it in the system's database.
    This endpoint is essential for user registration and onboarding.

    Please note that currently endpoint is not protected.
    However, if there are a lot of spam requests, the endpoint will be blocked or limited.
    """
    service: CreateUserService = CreateUserService(
        request_data=data,
    )
    return await service()


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=GetUserMeResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    name="user_me",
)
async def get_me(
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> GetUserMeResponse:
    """Get user details.

    Retrieve authenticated user profile information, including username, email, and account details.
    Personalize user experiences within the application using the JSON response containing user-specific data.
    """
    service: GetUserMeService = GetUserMeService(token=token)
    return await service()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[ListUsersResponse],
    name="list_users",
)
async def list_users(
    query: Annotated[
        str | None,
        Query(
            alias="query",
            description="Search by username.",
            min_length=1,
            max_length=128,
        ),
    ] = None,
) -> Page[ListUsersResponse]:
    """List users.

    Retrieve users. Search by username.
    """
    service: ListUsersService = ListUsersService(
        offset=0,
        limit=20,
        query=query,
    )
    return await service()


@router.put(
    "",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "No data to update.",
        },
    },
    name="update_user",
)
async def update_user(
    token: Annotated[str, Depends(_oauth2_scheme)],
    data: UpdateUserRequest,
) -> UpdateUserResponse:
    """Update user details.

    This endpoint is crucial for users to manage and maintain accurate profile information,
    often including authentication and authorization checks for security.
    """
    service: UpdateUserService = UpdateUserService(
        token=token,
        request_data=data,
    )
    return await service()


@router.post(
    "/ddd",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User deletion is currently disabled.",
        },
    },
    name="request_user_deletion",
)
async def request_user_deletion(
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> None:
    service: RequestUserDeletionService = RequestUserDeletionService(token=token)
    return await service()


@router.post(
    "/confirmations/resend",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "User already activated.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedResponse,
        },
    },
    name="resend_user_confirmation",
)
async def resend_user_confirmation(
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> None:
    """Resend user confirmation.

    If the confirmation message is not delivered or got lost, user can request another message.
    """
    service: ResendUserConfirmationService = ResendUserConfirmationService(
        token=token,
    )
    return await service()


@router.post(
    "/passwords/request-change",
    status_code=status.HTTP_202_ACCEPTED,
    name="request_change_user_password",
)
async def request_change_user_password(
    data: RequestChangeUserPasswordRequest,
) -> None:
    """Request password change."""
    service: RequestChangeUserPasswordService = RequestChangeUserPasswordService(
        request_data=data,
    )
    return await service()
