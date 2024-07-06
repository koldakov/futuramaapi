import random
from operator import add
from typing import ClassVar, Self

from fastapi import Request
from pydantic import Field, HttpUrl, computed_field, field_serializer, field_validator
from sqlalchemy.ext.asyncio.session import AsyncSession

from futuramaapi.core import settings
from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.mixins.pydantic import BaseModelDatabaseMixin
from futuramaapi.repositories.models import SecretMessageModel
from futuramaapi.routers.exceptions import ModelNotFoundError


class SecretMessageCreateRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=8192,
    )

    @field_validator("text")
    @classmethod
    def encrypt_text(cls, value: str, /) -> str:
        return cls.encryptor.encrypt(value.encode()).decode()


class SecretMessageCreateResponse(BaseModel):
    url: str

    @computed_field(  # type: ignore[misc]
        return_type=HttpUrl,
    )
    @property
    def message_link(self) -> HttpUrl:
        return settings.build_url(
            path=self.url,
            is_static=False,
        )


class SecretMessage(BaseModel, BaseModelDatabaseMixin):
    model: ClassVar[type[SecretMessageModel]] = SecretMessageModel
    max_visit_counter: ClassVar[int] = 1
    _words_amount: ClassVar[int] = 3
    _words: ClassVar[tuple[str, ...]] = (
        "hut",
        "allocation",
        "style",
        "bishop",
        "housewife",
        "button",
        "coat",
        "apparatus",
        "secure",
        "unfair",
        "advance",
        "stir",
        "perfect",
        "spot",
        "wardrobe",
        "widen",
        "pack",
        "offspring",
        "railroad",
        "trust",
        "auditor",
        "slippery",
        "reference",
        "cake",
        "wreck",
        "owner",
        "fool",
        "ambiguous",
        "offend",
        "landowner",
        "lesson",
        "maximum",
        "fluctuation",
        "bet",
        "inject",
        "analysis",
        "verdict",
        "gem",
        "assignment",
        "salt",
        "troop",
        "assertive",
        "approach",
        "garbage",
        "post",
        "vessel",
        "mess",
        "promote",
        "rubbish",
        "cassette",
        "tropical",
        "bend",
        "allow",
        "guide",
        "trail",
        "chorus",
        "integrity",
        "retiree",
        "kill",
        "reality",
        "chemistry",
        "houseplant",
        "nervous",
        "penalty",
        "wine",
        "literature",
        "strap",
        "add",
        "service",
        "north",
        "refund",
        "count",
        "science",
        "afford",
        "systematic",
        "cut",
        "interference",
        "electronics",
        "entertainment",
        "bake",
        "middle",
        "brink",
        "pound",
        "sun",
        "undermine",
        "bus",
        "term",
        "traffic",
        "brilliance",
        "marathon",
        "favourite",
        "driver",
        "arrow",
        "payment",
        "coffin",
        "patrol",
        "redeem",
        "ideology",
        "chicken",
        "general",
        "vein",
        "whip",
        "conception",
        "define",
        "cancer",
        "peanut",
        "snub",
        "anxiety",
        "strong",
        "housewife",
        "smash",
        "feather",
        "visit",
        "freighter",
        "prescription",
        "royalty",
        "flavor",
        "ring",
        "circumstance",
        "spare",
        "calorie",
        "welcome",
        "barrel",
        "liberal",
        "abolish",
        "lighter",
        "garage",
        "education",
        "mild",
        "error",
        "routine",
        "rehabilitation",
        "blast",
        "traffic",
        "sacred",
        "illness",
        "offer",
        "concentration",
        "quality",
        "regulation",
        "sandwich",
        "empire",
        "line",
        "earthquake",
        "musical",
        "confuse",
        "colony",
        "jaw",
        "he",
        "haunt",
        "ordinary",
        "mention",
        "formula",
        "law",
        "sensitivity",
        "kettle",
        "crown",
        "press",
        "race",
        "fragment",
        "install",
        "eject",
        "wild",
        "eyebrow",
        "hypothesis",
        "definite",
        "blonde",
        "entertain",
        "tube",
        "deal",
        "horseshoe",
        "miscarriage",
        "bathtub",
        "chip",
        "shell",
        "federation",
        "pierce",
        "contraction",
        "lamp",
        "patent",
        "hotdog",
        "file",
        "wisecrack",
        "stem",
        "dorm",
        "beer",
        "sacred",
        "liability",
        "mainstream",
        "linen",
        "dilute",
        "gutter",
        "avenue",
        "sniff",
        "government",
        "expect",
        "system",
        "divide",
        "gallery",
        "bill",
    )

    id: int
    visit_counter: int
    ip_address: str
    url: str
    text: str

    @field_serializer("text")
    @classmethod
    def encrypt_text(cls, value: str, /) -> str:
        return cls.encryptor.decrypt(value.encode()).decode()

    @classmethod
    def _get_random_words(cls) -> str:
        return " ".join(
            random.sample(
                cls._words,
                cls._words_amount,
            ),
        )

    @classmethod
    async def get_once(
        cls,
        session: AsyncSession,
        request: Request,
        url: str,
        /,
    ) -> Self:
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
        )

        if message.visit_counter <= cls.max_visit_counter:
            response: SecretMessage = message.copy(deep=True)
            response.ip_address = request.client.host

            await message.update(
                session,
                None,
                ip_address=request.client.host,
                text=cls.encryptor.encrypt(cls._get_random_words().encode()).decode(),
            )

            return response

        return message
