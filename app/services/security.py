from fastapi.param_functions import Body
from pydantic import BaseModel
from typing_extensions import Annotated, Doc


class UnauthorizedResponse(BaseModel):
    detail: str


class OAuth2PasswordRequestJson:
    def __init__(
        self,
        *,
        username: Annotated[
            str,
            Body(),
            Doc(
                """
                `username` string. The OAuth2 spec requires the exact field name
                `username`.
                """
            ),
        ],
        password: Annotated[
            str,
            Body(),
            Doc(
                """
                `password` string. The OAuth2 spec requires the exact field name
                `password".
                """
            ),
        ],
    ):
        self.username = username
        self.password = password
