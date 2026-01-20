from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.models import AuthSessionModel
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.rest.users.dependencies import cookie_user_from_form_data, user_from_cookies
from futuramaapi.routers.rest.users.schemas import User

router = APIRouter()


@router.post(
    "/auth",
    include_in_schema=False,
    name="auth_user",
)
async def auth_user(
    user: User | None = Depends(cookie_user_from_form_data),  # noqa: B008
) -> RedirectResponse:
    if user is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)

    response: RedirectResponse = RedirectResponse(
        "/",
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie(
        User.cookie_auth_key,
        value=user._cookie_session,
        expires=user.cookie_expiration_time,
    )
    return response


@router.post(
    "/logout",
    include_in_schema=False,
    name="user_logout",
)
async def cookie_logout_user(
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
    user: User | None = Depends(user_from_cookies),  # noqa: B008
) -> RedirectResponse:
    if user is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)

    if user._cookie_session is not None:
        await AuthSessionModel.do_expire(session, user._cookie_session)

    response: RedirectResponse = RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(User.cookie_auth_key)
    return response
