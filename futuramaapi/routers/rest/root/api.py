from operator import add

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.repositories.models import AuthSessionModel
from futuramaapi.repositories.session import get_async_session
from futuramaapi.routers.exceptions import ModelNotFoundError
from futuramaapi.routers.rest.users.dependencies import cookie_user_from_form_data, user_from_cookies
from futuramaapi.routers.rest.users.schemas import Link, User

from .schemas import About, Root, SiteMap, UserAuth

router = APIRouter()


@router.get(
    "/health",
    tags=[
        "health",
    ],
    include_in_schema=False,
)
def health() -> Response:
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/favicon.ico",
    include_in_schema=False,
)
async def favicon():
    return FileResponse("favicon.ico")


@router.get(
    "/swagger",
    include_in_schema=False,
    name="swagger",
)
async def get_swagger():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Swagger Playground | Futurama API",
        swagger_favicon_url="/favicon.ico",
    )


@router.get(
    "/docs",
    include_in_schema=False,
    name="redoc_html",
)
async def get_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Documentation | Futurama API",
        redoc_favicon_url="/favicon.ico",
    )


@router.get(
    "/",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
    name="root",
)
async def get_root(
    request: Request,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Response:
    obj: Root = await Root.from_request(session, request)
    return await obj.get_response(request)


@router.get(
    "/about",
    include_in_schema=False,
    name="about",
)
async def about(
    request: Request,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> Response:
    obj: About = await About.from_request(session, request)
    return await obj.get_response(request)


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
    "/robots.txt",
    include_in_schema=False,
)
async def robots():
    return FileResponse("robots.txt")


@router.get(
    "/s/{shortened}",
    include_in_schema=False,
    name="user_link_redirect",
)
async def user_link_redirect(
    shortened: str,
    session: AsyncSession = Depends(get_async_session),  # noqa: B008
) -> RedirectResponse:
    try:
        link: Link = await Link.get(session, shortened, field=Link.model.shortened)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        ) from None
    await link.update(
        session,
        None,
        counter=add(link.counter, 1),
    )
    return RedirectResponse(link.url)


@router.get(
    "/sitemap.xml",
    include_in_schema=False,
)
async def get_sitemap(
    request: Request,
) -> Response:
    obj: SiteMap = await SiteMap.from_request(request)
    return await obj.get_response()
