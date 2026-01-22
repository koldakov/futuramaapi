from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from futuramaapi.routers.rest.users.dependencies import cookie_user_from_form_data
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
