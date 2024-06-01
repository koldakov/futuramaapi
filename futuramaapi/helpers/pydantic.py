import json
import uuid
from typing import Any, ClassVar

import pydash
from pydantic import BaseModel as BaseModelOrig
from pydantic import ConfigDict, Field, SecretStr
from pydash import camel_case

from futuramaapi.helpers.hashers import PasswordHasherBase, hasher


class BaseModel(BaseModelOrig):
    hasher: ClassVar[PasswordHasherBase] = hasher

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=camel_case,
    )

    def to_dict(self, *, by_alias: bool = True, reveal_secrets: bool = False, exclude_unset=False) -> dict:
        result: dict = json.loads(self.model_dump_json(by_alias=by_alias, exclude_unset=exclude_unset))
        if reveal_secrets is False:
            return result

        secret_dict: dict = {}
        name: str
        for name in self.model_fields_set:
            field: Any = getattr(self, name)
            if isinstance(field, SecretStr):
                secret_dict.update(
                    {
                        name: field.get_secret_value(),
                    }
                )
        return pydash.merge(result, secret_dict)


class BaseTokenModel(BaseModel):
    def refresh_nonce(self) -> None:
        self.nonce = self._get_nonce()

    @staticmethod
    def _get_nonce() -> str:
        return uuid.uuid4().hex

    nonce: str = Field(default_factory=_get_nonce)
