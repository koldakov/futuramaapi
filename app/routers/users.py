from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import Annotated

from app.repositories.sessions import get_async_session
from app.services.auth import oauth2_scheme
from app.services.security import TokenData
from app.services.users import (
    User,
    UserAdd,
    process_add_user,
    process_get_me,
)

router = APIRouter(prefix="/users")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    name="user",
)
async def add_user(
    body: UserAdd,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Create User.

    The user add endpoint is an API function allowing the creation of new user accounts.
    It receives user details via HTTP requests, validates the information,
    and stores it in the system's database.
    This endpoint is essential for user registration and onboarding.

    Please note that currently endpoint is not protected.
    However, if there are a lot of spam requests, the endpoint will be blocked or limited.
    """
    return await process_add_user(body, session)


@router.get(
    "/me",
    response_model=User,
    name="user_me",
)
async def get_me(
    token: Annotated[TokenData, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Get user details.

    Retrieve authenticated user profile information, including username, email, and account details.
    Personalize user experiences within the application using the JSON response containing user-specific data.
    """
    return await process_get_me(token, session)
