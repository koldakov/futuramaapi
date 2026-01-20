from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.models import AuthSessionModel
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.rest.users.dependencies import cookie_user_from_form_data, user_from_cookies
from futuramaapi.routers.rest.users.schemas import User

from .schemas import Changelog, UserAuth

router = APIRouter()


@router.get(
    "/auth",
    include_in_schema=False,
    name="user_auth",
)
async def user_auth(
    request: Request,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
    user: User | None = Depends(user_from_cookies),  # noqa: B008
) -> Response:
    if user is not None:
        return RedirectResponse("/")

    obj: UserAuth = await UserAuth.from_request(session, request)
    return await obj.get_response(request)


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


@router.get(
    "/changelog",
    include_in_schema=False,
    name="changelog",
)
async def get_changelog(
    request: Request,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
):
    obj: Changelog = await Changelog.from_request(session, request)
    return await obj.get_response(request)
