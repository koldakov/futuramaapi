from typing import ClassVar, Self

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from futuramaapi.helpers.pydantic import BaseModel, Field
from futuramaapi.mixins.pydantic import BaseModelTemplateMixin
from futuramaapi.repositories.base import FilterStatementKwargs
from futuramaapi.routers.characters.schemas import Character
from futuramaapi.routers.users.schemas import User


class Root(BaseModel, BaseModelTemplateMixin):
    characters: list[Character]
    user_count: int = Field(alias="user_count")

    template_name: ClassVar[str] = "index.html"

    @classmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self:
        user_count: int = await User.count(session)
        characters: list[Character] = await Character.filter(
            session,
            FilterStatementKwargs(
                limit=6,
            ),
        )

        return cls(
            characters=characters,
            user_count=user_count,
        )


class About(BaseModel, BaseModelTemplateMixin):
    template_name: ClassVar[str] = "about.html"

    @classmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self:
        return cls()


class UserAuth(BaseModel, BaseModelTemplateMixin):
    template_name: ClassVar[str] = "auth.html"

    @classmethod
    async def from_request(cls, session: AsyncSession, request: Request, /) -> Self:
        return cls()
