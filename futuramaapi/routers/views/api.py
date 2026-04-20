from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request, Response, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from futuramaapi.routers.services.about.get_about import GetAboutService
from futuramaapi.routers.services.auth.auth_cookie_session_user import AuthCookieSessionUserService
from futuramaapi.routers.services.auth.get_user_auth import GetUserAuthService, UserAuthMessageType
from futuramaapi.routers.services.auth.get_user_signup import GetUserSignupService, UserSignupMessageType
from futuramaapi.routers.services.auth.logout_cookie_session_user import LogoutCookieSessionUserService
from futuramaapi.routers.services.auth.signup_cookie_session_user import SignupCookieSessionUserService
from futuramaapi.routers.services.changelog.get_changelog import GetChangelogService
from futuramaapi.routers.services.index.get_index import GetIndexService
from futuramaapi.routers.services.sitemaps.get_sitemap import GetSiteMapService

router: APIRouter = APIRouter()


@router.get(
    "/favicon.ico",
)
async def favicon() -> FileResponse:
    return FileResponse("favicon.ico")


@router.get(
    "/health",
)
def health() -> Response:
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/swagger",
    name="swagger",
)
async def get_swagger() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Swagger Playground | Futurama API",
        swagger_favicon_url="/favicon.ico",
    )


@router.get(
    "/docs",
    name="redoc_html",
)
async def get_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Documentation | Futurama API",
        redoc_favicon_url="/favicon.ico",
    )


@router.get(
    "/robots.txt",
)
async def robots() -> FileResponse:
    return FileResponse("robots.txt")


@router.get(
    "/sitemap.xml",
)
async def get_sitemap() -> Response:
    service: GetSiteMapService = GetSiteMapService()
    return await service()


@router.get(
    "/",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
    name="get_index",
)
async def get_index(
    request: Request,
) -> Response:
    service: GetIndexService = GetIndexService(
        context={
            "request": request,
        },
    )
    return await service()


@router.get(
    "/about",
    include_in_schema=False,
    name="about",
)
async def about(
    request: Request,
) -> Response:
    service: GetAboutService = GetAboutService(
        context={
            "request": request,
        },
    )
    return await service()


@router.get(
    "/changelog",
    include_in_schema=False,
    name="changelog",
)
async def get_changelog(
    request: Request,
):
    service: GetChangelogService = GetChangelogService(
        context={
            "request": request,
        },
    )
    return await service()


@router.get(
    "/auth",
    include_in_schema=False,
    name="user_auth",
)
async def user_auth(
    request: Request,
    message_type: Annotated[
        UserAuthMessageType | None,
        Query(
            alias="messageType",
        ),
    ] = None,
) -> Response:
    service: GetUserAuthService = GetUserAuthService(
        message_type=message_type,
        context={
            "request": request,
        },
    )
    return await service()


@router.post(
    "/logout",
    include_in_schema=False,
    name="logout_cookie_session_user",
)
async def logout_cookie_session_user(
    request: Request,
) -> RedirectResponse:
    service: LogoutCookieSessionUserService = LogoutCookieSessionUserService(
        context={
            "request": request,
        },
    )
    return await service()


@router.get(
    "/signup",
    include_in_schema=False,
    name="user_signup",
)
async def user_signup(
    request: Request,
    message_type: Annotated[
        UserSignupMessageType | None,
        Query(
            alias="messageType",
        ),
    ] = None,
) -> Response:
    service: GetUserSignupService = GetUserSignupService(
        message_type=message_type,
        context={
            "request": request,
        },
    )
    return await service()


@router.post(
    "/signup",
    include_in_schema=False,
    name="signup_cookie_session_user",
)
async def signup_cookie_session_user(  # noqa: PLR0913
    request: Request,
    name: Annotated[str, Form()] = "",
    surname: Annotated[str, Form()] = "",
    email: Annotated[str, Form()] = "",
    username: Annotated[str, Form()] = "",
    password: Annotated[str, Form()] = "",
) -> RedirectResponse:
    if not all([name.strip(), surname.strip(), email.strip(), username.strip(), password]):
        return RedirectResponse(
            url=f"/signup?messageType={UserSignupMessageType.validation_error}",
            status_code=status.HTTP_302_FOUND,
        )
    try:
        service: SignupCookieSessionUserService = SignupCookieSessionUserService(
            name=name,
            surname=surname,
            email=email,
            username=username,
            password=password,
            context={
                "request": request,
            },
        )
    except ValidationError:
        return RedirectResponse(
            url=f"/signup?messageType={UserSignupMessageType.validation_error}",
            status_code=status.HTTP_302_FOUND,
        )
    return await service()


@router.post(
    "/auth",
    include_in_schema=False,
    name="auth_cookie_session_user",
)
async def auth_cookie_session_user(
    request: Request,
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
) -> RedirectResponse:
    service: AuthCookieSessionUserService = AuthCookieSessionUserService(
        username=form_data.username,
        password=form_data.password,
        context={
            "request": request,
        },
    )
    return await service()
