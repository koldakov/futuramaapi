import json
import logging
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, Self
from uuid import UUID

import jwt
from fastapi import Request
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from pydantic import HttpUrl, model_validator
from pydantic.main import IncEx
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement
from starlette.templating import _TemplateResponse

from futuramaapi.__version__ import __version__
from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.helpers.templates import templates
from futuramaapi.repositories.base import Base, FilterStatementKwargs, ModelAlreadyExistsError, ModelDoesNotExistError
from futuramaapi.repositories.session import session_manager
from futuramaapi.routers.exceptions import ModelExistsError, ModelNotFoundError, UpdateArgsNotDefined

if TYPE_CHECKING:
    from sqlalchemy import Select

    from futuramaapi.routers.users.schemas import User

logger = logging.getLogger(__name__)


class _PydanticSanityCheck[Model: BaseModel]:  # type: ignore[valid-type]
    _required_methods: ClassVar[tuple[str, ...]] = (
        "model_validate",
        "model_dump_json",
        "model_dump",
    )

    @classmethod
    @abstractmethod
    def model_validate(
        cls: type[Model],  # type: ignore[name-defined]
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> Model:  # type: ignore[name-defined]
        ...

    @abstractmethod
    def model_dump_json(  # noqa: PLR0913
        self,
        *,
        indent: int | None = None,
        include: IncEx = None,
        exclude: IncEx = None,
        context: dict[str, Any] | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> str: ...

    @abstractmethod
    def model_dump(  # noqa: PLR0913
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        context: dict[str, Any] | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]: ...

    def __init_subclass__(cls):
        """
        Sanity check.
        """
        if not all(hasattr(cls, attr) for attr in cls._required_methods):
            raise RuntimeError(f"Class {cls.__name__} should be inherited from ``pydantic.BaseModel``.")


class BaseModelDatabaseMixin[Model: BaseModel](ABC, _PydanticSanityCheck):  # type: ignore[valid-type]
    model: ClassVar[type[Base]]

    id: int

    @classmethod
    async def count(cls, session: AsyncSession, /) -> int:
        return await cls.model.count(session)

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        val: int | str | UUID,
        /,
        *,
        field: InstrumentedAttribute | None = None,
        extra_where: list[ColumnElement[bool]] | None = None,
    ) -> Self:
        try:
            obj: Base = await cls.model.get(session, val, field=field, extra_where=extra_where)
        except ModelDoesNotExistError as err:
            logger.info(
                "Model does not exist",
                extra={
                    "value": val,
                    "err": err,
                },
            )
            raise ModelNotFoundError() from None
        return cls.model_validate(obj)

    @classmethod
    async def paginate(
        cls,
        session: AsyncSession,
        /,
        filter_params: FilterStatementKwargs | None = None,
    ) -> Page[Model]:  # type: ignore[name-defined]
        if filter_params is None:
            filter_params = FilterStatementKwargs(
                offset=0,
                limit=20,
            )

        statement: Select[tuple[Base]] = cls.model.get_filter_statement(filter_params)
        return await paginate(
            session,
            statement,
        )

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: BaseModel,
        /,
        extra_fields: dict[
            str,
            Any,
        ]
        | None = None,
    ) -> Self:
        try:
            obj: Base = await cls.model.create(session, data, extra_fields=extra_fields)
        except ModelAlreadyExistsError as err:
            logger.info(
                "Model already exists",
                extra={
                    "data": data.model_dump(),
                    "err": err,
                },
            )
            raise ModelExistsError() from None
        return cls.model_validate(obj)

    async def update(self, session: AsyncSession, data: BaseModel | None, /, **kwargs) -> None:
        if data is None and not kwargs:
            raise UpdateArgsNotDefined() from None

        data_dict: dict[str, str] = {}
        if data is not None:
            data_dict = data.to_dict(by_alias=False, reveal_secrets=True, exclude_unset=True)
        if kwargs:
            data_dict.update(kwargs)
        obj: Base = await self.model.update(session, self.id, data_dict)

        updated: BaseModel = self.model_validate(obj)
        for field in updated.model_fields_set:
            val: Any = getattr(updated, field)
            setattr(self, field, val)

    @classmethod
    async def filter(cls, session: AsyncSession, kwargs: FilterStatementKwargs, /) -> list[Self]:
        return [cls.model_validate(character) for character in await cls.model.filter(session, kwargs)]


class TokenBaseError(Exception): ...


class DecodedTokenError(TokenBaseError): ...


class BaseModelTokenMixin(ABC, _PydanticSanityCheck):
    @staticmethod
    def _get_payload(payload: dict, exp: datetime, /) -> dict:
        cleaned_payload: dict = deepcopy(payload)
        cleaned_payload.update(
            {
                "exp": exp,
            }
        )

        return cleaned_payload

    def tokenize(self, exp: int, /, *, algorithm="HS256") -> str:
        """Tokenizes the given model.

        Args:
            exp (int): Expiration time in seconds.
            algorithm (str): Tokenize algorithm. Default is HS256.

        Returns:
            str: JWT.
        """
        exp_time: datetime = datetime.now(UTC) + timedelta(seconds=exp)
        payload = json.loads(self.model_dump_json(by_alias=True))
        return jwt.encode(
            self._get_payload(payload, exp_time),
            settings.secret_key,
            algorithm=algorithm,
        )

    @classmethod
    def decode(cls, token: str, /, *, algorithm="HS256"):
        try:
            token_: dict = jwt.decode(token, key=settings.secret_key, algorithms=[algorithm])
        except (ExpiredSignatureError, InvalidSignatureError, InvalidTokenError):
            raise DecodedTokenError() from None
        return cls(**token_)


class BaseModelTemplateMixin(ABC, _PydanticSanityCheck):
    template_name: ClassVar[str]

    async def _get_user_from_request(self, request: Request, /) -> Optional["User"]:
        from futuramaapi.routers.users.schemas import User

        try:
            session_id: str = request.cookies[User.cookie_auth_key]
        except KeyError:
            return None

        async with session_manager.session() as session:
            try:
                return await User.from_cookie_session_id(session, session_id)
            except ModelNotFoundError:
                return None

    async def get_context(self, request: Request, *, extra_context: dict[str, Any] | None = None) -> dict:
        user: "User" | None = await self._get_user_from_request(request)
        context: dict = {
            **self.model_dump(),
            "version": __version__,
            "current_user": user,
        }
        if extra_context:
            context.update(extra_context)
        return context

    async def get_response(
        self,
        request: Request,
        /,
        *,
        template_name: str | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> _TemplateResponse:
        if template_name is None:
            template_name = self.template_name

        return templates.TemplateResponse(
            request,
            template_name,
            context=await self.get_context(request, extra_context=extra_context),
        )

    @classmethod
    @abstractmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self: ...


class TemplateBodyMixin(ABC, _PydanticSanityCheck):
    class _User(BaseModel):
        id: int
        name: str
        surname: str

    user: _User
    url: HttpUrl = HttpUrl.build(
        scheme="https",
        host=settings.trusted_host,
    )
    expiration_time: ClassVar[int] = 3 * 24 * 60 * 60

    @abstractmethod
    @model_validator(mode="after")
    def build_confirmation_url(self) -> Self: ...

    @property
    @abstractmethod
    def signature(self) -> str: ...

    @classmethod
    def from_user(cls, user: "User", /) -> Self:
        return cls(  # type: ignore[call-arg]
            user=user.model_dump(),
        )
