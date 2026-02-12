import json
from typing import Any, ClassVar

import pydash
from cryptography.fernet import Fernet
from pydantic import BaseModel as BaseModelOrig
from pydantic import ConfigDict, SecretStr
from pydash import camel_case

from futuramaapi.core import settings
from futuramaapi.helpers.hashers import PasswordHasherBase, hasher


class BaseModel(BaseModelOrig):
    hasher: ClassVar[PasswordHasherBase] = hasher
    encryptor: ClassVar[Fernet] = settings.fernet

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=camel_case,
    )

    def to_dict(self, *, by_alias: bool = True, reveal_secrets: bool = False, exclude_unset=False) -> dict:
        result: dict = json.loads(self.model_dump_json(by_alias=by_alias, exclude_unset=exclude_unset))
        if not reveal_secrets:
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
