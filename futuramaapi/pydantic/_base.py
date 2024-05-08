from pydantic import BaseModel as BaseModelOrig
from pydantic import ConfigDict

from futuramaapi.utils.helpers import to_camel


class BaseModel(BaseModelOrig):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )
