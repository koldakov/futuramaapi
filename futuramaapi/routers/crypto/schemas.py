from operator import add
from typing import ClassVar, Self

from fastapi import Request
from pydantic import Field
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.mixins.pydantic import BaseModelDatabaseMixin
from futuramaapi.repositories.models import SecretMessageModel
from futuramaapi.routers.exceptions import ModelNotFoundError


class SecretMessageCreateRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=8192,
    )


class BaseSecretMessageError(Exception): ...


class SecretMessageBase(BaseModel):
    visit_counter: int
    id: int
    ip_address: str
    url: str


class HiddenSecretMessage(SecretMessageBase): ...


class SecretMessage(SecretMessageBase, BaseModelDatabaseMixin):
    model: ClassVar[type[SecretMessageModel]] = SecretMessageModel
    max_visit_counter: ClassVar[int] = 2

    text: str

    @classmethod
    async def get_once(
        cls,
        session: AsyncSession,
        request: Request,
        url: str,
        /,
    ) -> Self | HiddenSecretMessage:
        """
        3 requests to the DB.
        I need to forget about creating ORM and use sqlalchemy directly...
        """
        try:
            message: SecretMessage = await SecretMessage.get(
                session,
                url,
                field=SecretMessageModel.url,
            )
        except ModelNotFoundError:
            raise

        await message.update(
            session,
            None,
            visit_counter=add(message.visit_counter, 1),
            ip_address=request.client.host,
        )

        if message.visit_counter >= cls.max_visit_counter:
            return HiddenSecretMessage(**message.model_dump())

        await message.update(
            session,
            None,
            ip_address=request.client.host,
        )

        return message
