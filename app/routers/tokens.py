from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.repositories.sessions import get_async_session
from app.services.security import OAuth2PasswordRequestJson, UnauthorizedResponse
from app.services.tokens import (
    Token,
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
    return await process_token_auth_user(session, form_data)
