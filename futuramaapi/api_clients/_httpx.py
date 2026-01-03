from __future__ import annotations

from http import HTTPStatus
from typing import Any, TypedDict

import httpx

from ._base import (
    ApiClientConnectionError,
    ApiClientConnectTimeoutError,
    ApiClientProxyError,
    ApiClientReadTimeoutError,
    ApiClientTooManyRedirectsError,
    BaseClient,
    HTTPVersion,
    RequestData,
    ResponseData,
)


class HTTPKwargs(TypedDict):
    http1: bool
    http2: bool


class HTTPXClient(BaseClient):
    def __init__(  # noqa: PLR0913
        self,
        max_connections: int = 256,
        max_keepalive_connections: int | None = None,
        read_timeout: float | None = 5.0,
        write_timeout: float | None = 5.0,
        connect_timeout: float | None = 5.0,
        pool_timeout: float | None = 1.0,
        http_version: HTTPVersion = HTTPVersion.HTTP1_1,
        proxy: str | httpx.Proxy | httpx.URL | None = None,
        httpx_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._max_connections: int = max_connections
        self._max_keepalive_connections: int | None = max_keepalive_connections
        self._read_timeout: float | None = read_timeout
        self._write_timeout: float | None = write_timeout
        self._connect_timeout: float | None = connect_timeout
        self._pool_timeout: float | None = pool_timeout
        self._http_version: HTTPVersion = http_version
        self._proxy: str | httpx.Proxy | httpx.URL | None = proxy

        self.__client_kwargs: dict[str, Any] = {
            "timeout": self.timeout,
            "proxy": proxy,
            "limits": self.limits,
            **self.http_kwargs,
            **(httpx_kwargs or {}),
        }

        self._client: httpx.AsyncClient | None = None

    @property
    def http_kwargs(self) -> HTTPKwargs:
        http1: bool = self._http_version == HTTPVersion.HTTP1_1
        return {"http1": http1, "http2": not http1}

    @property
    def limits(self) -> httpx.Limits:
        return httpx.Limits(
            max_connections=self._max_connections,
            max_keepalive_connections=self._max_keepalive_connections,
        )

    @property
    def timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self._connect_timeout,
            read=self._read_timeout,
            write=self._write_timeout,
            pool=self._pool_timeout,
        )

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(**self.__client_kwargs)

    async def initialize(self) -> None:
        if self._client is not None:
            raise RuntimeError("Client already defined.")

        self._client = self._build_client()

    async def shutdown(self) -> None:
        if self._client is None:
            raise RuntimeError("Client is not defined.")

        await self._client.aclose()
        self._client = None

    def __get_extra_client_kwargs(self, request_data: RequestData, /) -> dict[str, Any]:
        extra_client_kwargs: dict[str, Any] = {}
        if request_data.timeout is not None:
            extra_client_kwargs.update(
                {
                    "timeout": httpx.Timeout(
                        connect=request_data.timeout.connect_timeout,
                        read=request_data.timeout.read_timeout,
                        write=request_data.timeout.write_timeout,
                        pool=request_data.timeout.pool_timeout,
                    ),
                },
            )
        return extra_client_kwargs

    async def request(
        self,
        request_data: RequestData,
        /,
    ) -> ResponseData:
        if self._client is None:
            raise RuntimeError("Client is not defined.")

        try:
            response: httpx.Response = await self._client.request(
                request_data.method,
                request_data.url,
                params=request_data.params,
                data=request_data.data,
                headers=request_data.headers,
                follow_redirects=request_data.follow_redirects,
                json=request_data.json,
                **self.__get_extra_client_kwargs(request_data),
            )
        except httpx.ConnectTimeout as exc:
            raise ApiClientConnectTimeoutError() from exc
        except httpx.ReadTimeout as exc:
            raise ApiClientReadTimeoutError() from exc
        except httpx.PoolTimeout as exc:
            raise ApiClientConnectTimeoutError() from exc
        except httpx.ProxyError as exc:
            raise ApiClientProxyError() from exc
        except httpx.TooManyRedirects as exc:
            raise ApiClientTooManyRedirectsError() from exc
        except httpx.NetworkError as exc:
            raise ApiClientConnectionError() from exc
        except httpx.HTTPError as exc:
            raise ApiClientConnectionError() from exc

        return ResponseData(
            status=HTTPStatus(response.status_code),
            content=response.content,
            headers=response.headers,
            elapsed=response.elapsed,
        )
