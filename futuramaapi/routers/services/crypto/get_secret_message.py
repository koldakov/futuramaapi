import random
from dataclasses import dataclass
from typing import ClassVar

from fastapi import HTTPException, Request, status
from pydantic import field_serializer
from sqlalchemy import Row, RowMapping, Select, case, select, update
from sqlalchemy.exc import NoResultFound

from futuramaapi.helpers.pydantic import BaseModel
from futuramaapi.repositories.models import SecretMessageModel
from futuramaapi.routers.services import BaseSessionService


class GetSecretMessageResponse(BaseModel):
    id: int
    visit_counter: int
    ip_address: str
    url: str
    text: str

    @field_serializer("text")
    @classmethod
    def encrypt_text(cls, value: str, /) -> str:
        return cls.encryptor.decrypt(value.encode()).decode()


@dataclass(frozen=True)
class SecretMessageRow:
    id: int
    url: str
    text: str
    visit_counter: int
    ip_address: str


class GetSecretMessageService(BaseSessionService[GetSecretMessageResponse]):
    url: str

    _max_visit_counter: ClassVar[int] = 1
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

    def _get_random_words(self) -> str:
        return " ".join(
            random.sample(
                self._words,
                self._words_amount,
            ),
        )

    def _get_statement(
        self,
        request: Request,
        /,
    ) -> Select[tuple[RowMapping]]:
        randomized_text: str = self.encryptor.encrypt(self._get_random_words().encode()).decode()

        secret_message_source = (
            select(
                SecretMessageModel.id,
                SecretMessageModel.url,
                SecretMessageModel.text,
                SecretMessageModel.visit_counter,
            )
            .where(SecretMessageModel.url == self.url)
            .cte("secret_message_source")
        )

        updated_secret_message = (
            update(SecretMessageModel)
            .where(SecretMessageModel.id == secret_message_source.c.id)
            .values(
                visit_counter=SecretMessageModel.visit_counter + 1,
                ip_address=case(
                    (
                        SecretMessageModel.visit_counter < self._max_visit_counter,
                        request.client.host,
                    ),
                    else_=SecretMessageModel.ip_address,
                ),
                text=case(
                    (
                        SecretMessageModel.visit_counter < self._max_visit_counter,
                        randomized_text,
                    ),
                    else_=SecretMessageModel.text,
                ),
            )
            .returning(
                SecretMessageModel.id,
                SecretMessageModel.visit_counter,
                SecretMessageModel.ip_address,
            )
            .cte("updated_secret_message")
        )

        return select(
            secret_message_source.c.id,
            secret_message_source.c.url,
            secret_message_source.c.text,
            updated_secret_message.c.visit_counter,
            updated_secret_message.c.ip_address,
        ).join(
            updated_secret_message,
            updated_secret_message.c.id == secret_message_source.c.id,
        )

    async def process(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> GetSecretMessageResponse:
        try:
            row: Row[tuple[SecretMessageRow]] = (await self.session.execute(self._get_statement(request))).one()
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not Found",
            ) from None

        await self.session.commit()

        return GetSecretMessageResponse.model_validate(row)
