from typing import ClassVar

from fastapi import Response

from futuramaapi.core import settings
from futuramaapi.routers.services import BaseService


class GetSiteMapService(BaseService[Response]):
    _header: ClassVar[str] = '<?xml version="1.0" encoding="UTF-8"?>'
    _media_type: ClassVar[str] = "application/xml"
    _url_tag: ClassVar[str] = """<url><loc>%s</loc></url>"""
    _url_set_tag: ClassVar[str] = """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>"""

    @property
    def urls(self) -> list[str]:
        from futuramaapi.apps import app  # noqa: PLC0415

        return [url.path for url in app.public_urls]

    async def __call__(self, *args, **kwargs) -> Response:
        urls: str = ""
        for url in self.urls:
            urls += self._url_tag % settings.build_url(
                path=url,
                is_static=False,
            )
        return Response(
            content=f"""{self._header}{self._url_set_tag % urls}""",
            media_type=self._media_type,
        )
