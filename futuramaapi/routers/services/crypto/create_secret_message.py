from typing import ClassVar

from pydantic import Field, HttpUrl, computed_field, field_validator
from sqlalchemy import Result, insert
from sqlalchemy.sql.dml import ReturningInsert

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import SecretMessageModel
from futuramaapi.routers.services import BaseSessionService


class CreateSecretMessageRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=8192,
    )

    @field_validator("text")
    @classmethod
    def encrypt_text(cls, value: str, /) -> str:
        return cls.encryptor.encrypt(value.encode()).decode()


class CreateSecretMessageResponse(BaseModel):
    url: str

    _base_path: ClassVar[str] = "/api/crypto/secret_message/"

    @computed_field(  # type: ignore[misc]
        return_type=HttpUrl,
    )
    @property
    def message_link(self) -> HttpUrl:
        return settings.build_url(
            path=f"{self._base_path}{self.url}",
            is_static=False,
        )


class CreateSecretMessageService(BaseSessionService[CreateSecretMessageResponse]):
    request_data: CreateSecretMessageRequest

    @property
    def statement(self) -> ReturningInsert[tuple[str]]:
        return (
            insert(SecretMessageModel)
            .values(
                text=self.request_data.text,
                ip_address="",
            )
            .returning(SecretMessageModel.url)
        )

    async def process(self, *args, **kwargs) -> CreateSecretMessageResponse:
        result: Result[tuple[str]] = await self.session.execute(self.statement)
        await self.session.commit()

        return CreateSecretMessageResponse(url=result.scalar_one())
