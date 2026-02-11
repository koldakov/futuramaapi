from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from fastapi_pagination import Page

from futuramaapi.db import INT32
from futuramaapi.routers.services.links.create_link import (
    CreateLinkRequest,
    CreateLinkResponse,
    CreateLinkService,
)
from futuramaapi.routers.services.links.get_link import GetLinkResponse, GetLinkService
from futuramaapi.routers.services.links.list_links import (
    ListLinksResponse,
    ListLinksService,
)
from futuramaapi.security import oauth2_scheme

router = APIRouter(
    prefix="/links",
    tags=["Links"],
)


@router.post(
    "",
    name="create_link",
)
async def create_link(
    token: Annotated[str, Depends(oauth2_scheme)],
    data: CreateLinkRequest,
) -> CreateLinkResponse:
    """Generate shortened URL."""
    service: CreateLinkService = CreateLinkService(
        token=token,
        request_data=data,
    )
    return await service()


@router.get(
    "/{link_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetLinkResponse,
    name="get_link",
)
async def get_link(
    link_id: Annotated[
        int,
        Path(
            le=INT32,
        ),
    ],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> GetLinkResponse:
    service: GetLinkService = GetLinkService(
        token=token,
        link_id=link_id,
    )
    return await service()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[ListLinksResponse],
    name="list_links",
)
async def list_links(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Page[ListLinksResponse]:
    """Retrieve user links."""
    service: ListLinksService = ListLinksService(
        token=token,
        offset=0,
        limit=20,
    )
    return await service()
