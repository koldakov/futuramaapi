from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from datetime import timedelta
    from http import HTTPStatus
    from types import TracebackType

RT = TypeVar("RT", bound="BaseClient")


class HTTPVersion(StrEnum):
    HTTP1_1 = "1.1"
    HTTP2 = "2.0"


class HttpMethod(StrEnum):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


class ApiErrorType(StrEnum):
    connect_timeout = "connect_timeout"
    proxy_error = "proxy_error"
    read_timeout = "read_timeout"
    too_many_redirects = "too_many_redirects"
    connection_error = "connection_error"


class BaseApiClientError(Exception):
    """Base class for all API client errors.

    The `error_type` attribute defines the type of error according to ApiErrorType.
    All specific API client errors should inherit from this class.
    """

    error_type: ApiErrorType


class ApiClientConnectTimeoutError(BaseApiClientError):
    """Connection timeout error.

    Raised when the client fails to establish a connection to the server
    within the specified connect timeout.
    """

    error_type = ApiErrorType.connect_timeout


class ApiClientProxyError(BaseApiClientError):
    """Proxy error.

    Raised when a connection through the specified proxy fails.
    """

    error_type = ApiErrorType.proxy_error


class ApiClientReadTimeoutError(BaseApiClientError):
    """Read timeout error.

    Raised when the client successfully connects to the server,
    but the server does not send a response within the specified read timeout.
    """

    error_type = ApiErrorType.read_timeout


class ApiClientTooManyRedirectsError(BaseApiClientError):
    """Too many redirects error.

    Raised when the client exceeds the allowed number of redirects.
    """

    error_type = ApiErrorType.too_many_redirects


class ApiClientConnectionError(BaseApiClientError):
    """General connection error.

    Raised for other types of connection-related errors that do not fit
    into more specific categories like timeout or proxy errors.
    """

    error_type = ApiErrorType.connection_error


@dataclass
class RequestTimeout:
    connect_timeout: float | None = None
    read_timeout: float | None = None
    write_timeout: float | None = None
    pool_timeout: float | None = None


@dataclass
class RequestData:
    """Represents a single HTTP request.

    Attributes:
        url: The URL to send the request to.
        method: The HTTP method to use (GET, POST, etc.). Defaults to OPTIONS.
        params: Query parameters to include in the URL. Optional.
        data: Form or body data to send with the request. Optional.
        headers: HTTP headers to include with the request. Optional.
        timeout: Optional per-request timeout settings.
            If provided, these values override the default timeouts
            set in the client during initialization.
        follow_redirects: Whether the client should automatically follow HTTP redirects.
            Defaults to True.
        verify: Whether to verify SSL/TLS certificates.
            Defaults to True. Can be set to False for testing or internal services.
        json: JSON-serializable object to send as the request body. Optional.
    """

    url: str
    method: HttpMethod = HttpMethod.OPTIONS
    params: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
    timeout: RequestTimeout | None = None
    follow_redirects: bool = True
    verify: bool = True
    json: dict[str, Any] | None = None


@dataclass(frozen=True)
class ResponseData:
    """Represents the response from an HTTP request.

    Attributes:
        status: The HTTP status code of the response (e.g., 200, 404).
        content: The raw response body as bytes.
        headers: The HTTP headers returned by the server.
        elapsed: The time taken to complete the request as a timedelta.
    """

    status: HTTPStatus
    content: bytes
    headers: MutableMapping[str, Any]
    elapsed: timedelta


class BaseClient(
    AbstractAsyncContextManager["BaseClient"],
    ABC,
):
    """Abstract base class for an asynchronous HTTP client.

    Provides a standard interface for initializing, shutting down,
    and sending HTTP requests. Designed to be subclassed by
    concrete implementations (e.g., HTTPXClient).

    Features:
        - Async context manager support via __aenter__ and __aexit__.
          Ensures proper initialization and shutdown of the client.
        - Abstract methods `initialize`, `shutdown`, and `request`
          must be implemented by subclasses.
        - Central place to enforce consistent error handling, timeouts,
          and other request-level behaviors across all API clients.

    Usage:
        # Using async context manager (recommended)
        >>> async def foo():
        >>>     async with MyClient() as client:
        >>>         response = await client.request(request_data)

        # Manual initialization and shutdown
        >>> async def foo():
        >>>     client = MyClient()
        >>>     await client.initialize()
        >>>     response = await client.request(request_data)
        >>>     await client.shutdown()

    Notes:
        - `__aenter__` will call `initialize()` and automatically
          call `shutdown()` if initialization fails.
        - `__aexit__` ensures that `shutdown()` is always called
          when exiting the context manager.
    """

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def shutdown(self) -> None: ...

    @abstractmethod
    async def request(
        self,
        request_data: RequestData,
    ) -> ResponseData: ...

    async def __aenter__(self: RT) -> RT:
        try:
            await self.initialize()
        except Exception:
            await self.shutdown()
            raise
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.shutdown()
