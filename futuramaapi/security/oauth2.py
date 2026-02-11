from typing import ClassVar

from fastapi.security import OAuth2PasswordBearer as _OAuth2PasswordBearer


class OAuth2PasswordBearer(_OAuth2PasswordBearer):
    _token_url: ClassVar[str] = "/api/tokens/users/auth"  # noqa: S105

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, tokenUrl=self._token_url, **kwargs)


oauth2_scheme = OAuth2PasswordBearer()
