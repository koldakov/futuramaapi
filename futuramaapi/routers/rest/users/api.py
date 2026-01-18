from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories import INT32, FilterStatementKwargs
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError, UnauthorizedResponse

from .dependencies import from_form_signature, from_signature, from_token, password_from_form_data
from .schemas import (
    Link,
    LinkCreateRequest,
    PasswordChange,
    User,
    UserAlreadyActivatedError,
    UserPasswordChangeRequest,
    UserSearchResponse,
    UserUpdateRequest,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


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
    return await response.get_response(request)


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
    description="This endpoint is deprecated and will be removed in version 1.12.1. Please use `/api/links` instead.",
    deprecated=True,
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
    description="This endpoint is deprecated and will be removed in version 1.12.1. Please use `/api/links` instead.",
    deprecated=True,
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


@router.get(
    "/links/{link_id}",
    status_code=status.HTTP_200_OK,
    response_model=Link,
    name="user_link",
    description="This endpoint is deprecated and will be removed in version 1.12.1. "
    "Please use `/api/links/{link_id}` instead.",
    deprecated=True,
)
async def get_user_link(
    link_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
    user: Annotated[User, Depends(from_token)],
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Link:
    try:
        link: Link = await Link.get(
            session,
            link_id,
            extra_where=[Link.model.user_id == user.id],
        )
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        ) from None
    return link


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    response_model=Page[UserSearchResponse],
    name="user_search",
    summary="Deprecated list users endpoint",
    description="This endpoint is deprecated and will be removed in version 1.12.1. Please use `/api/users` instead.",
    deprecated=True,
)
async def search_user(
    query: Annotated[
        str | None,
        Query(
            alias="query",
            description="Search by username.",
            max_length=128,
        ),
    ] = None,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> UserSearchResponse:
    filter_params: FilterStatementKwargs = FilterStatementKwargs(
        offset=0,
        limit=20,
        extra={
            "query": query,
        },
    )
    return await UserSearchResponse.paginate(session, filter_params=filter_params)
