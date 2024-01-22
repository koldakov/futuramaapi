from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.users import (
    User,
    UserAdd,
    process_add_user,
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
