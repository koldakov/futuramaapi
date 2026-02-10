from typing import Literal

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import Field
from sqlalchemy import ColumnElement, Select, UnaryExpression, select

from futuramaapi.db.models import CharacterModel
from futuramaapi.routers.services import BaseSessionService

from .get_character import GetCharacterResponse


class ListCharactersResponse(GetCharacterResponse):
    pass


class ListCharactersService(BaseSessionService[Page[ListCharactersResponse]]):
    gender: str | None
    character_status: str | None
    species: str | None

    order_by: Literal["id"] = "id"
    direction: Literal["asc", "desc"] = "asc"
    query: str | None = Field(
        default=...,
        max_length=128,
    )

    @property
    def __where(self) -> list[ColumnElement[bool]]:
        where: list[ColumnElement[bool]] = []

        if self.gender is not None:
            if self.gender.startswith("!"):
                where.append(CharacterModel.gender != CharacterModel.CharacterGender[self.gender[1:].upper()])
            else:
                where.append(CharacterModel.gender == CharacterModel.CharacterGender[self.gender.upper()])

        if self.character_status is not None:
            if self.character_status.startswith("!"):
                where.append(CharacterModel.status != CharacterModel.CharacterStatus[self.character_status[1:].upper()])
            else:
                where.append(CharacterModel.status == CharacterModel.CharacterStatus[self.character_status.upper()])

        if self.species is not None:
            if self.species.startswith("!"):
                where.append(CharacterModel.species == CharacterModel.CharacterSpecies[self.species[1:].upper()])
            else:
                where.append(CharacterModel.species == CharacterModel.CharacterSpecies[self.species.upper()])

        if self.query is not None:
            where.append(CharacterModel.name.ilike(self.query))

        return where

    @property
    def __order_by(self) -> UnaryExpression[CharacterModel]:
        order_by = CharacterModel.str_to_field(self.order_by)
        if self.direction == "asc":
            return order_by.asc()

        return order_by.desc()

    @property
    def statement(self) -> Select[tuple[CharacterModel]]:
        statement: Select[tuple[CharacterModel]] = select(CharacterModel)
        return statement.where(*self.__where).order_by(self.__order_by)

    async def process(self, *args, **kwargs) -> Page[ListCharactersResponse]:
        return await paginate(
            self.session,
            self.statement,
        )
