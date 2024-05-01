import base64
import hashlib
import logging
import math
import secrets
from abc import ABC, abstractmethod
from collections.abc import Callable

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HasherBaseException(Exception):
    """Hasher Base Exception."""


class DecodedPassword(BaseModel):
    algorithm: str
    hash: str
    iterations: int
    salt: str


class PasswordHasherBase(ABC):
    algorithm: str | None = None
    salt_entropy: int = 128
    separator: str = "."
    random_string_chars: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    @staticmethod
    def pbkdf2(
        password: bytes,
        salt: bytes,
        iterations: int,
        /,
        *,
        dk_len: int | None = 0,
        digest: Callable | None = None,
    ):
        if digest is None:
            digest = hashlib.sha256
        dk_len = dk_len or None
        return hashlib.pbkdf2_hmac(digest().name, password, salt, iterations, dk_len)

    def get_random_string(
        self,
        length: int,
        /,
        *,
        allowed_chars: str | None = None,
    ):
        chars = allowed_chars if allowed_chars is not None else self.random_string_chars
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def compare(
        val1: bytes,
        val2: bytes,
        /,
    ) -> bool:
        return secrets.compare_digest(val1, val2)

    def salt(self) -> str:
        count = math.ceil(self.salt_entropy / math.log2(len(self.random_string_chars)))
        return self.get_random_string(count, allowed_chars=self.random_string_chars)

    @abstractmethod
    def verify(self, password, encoded, /) -> bool: ...

    def _check_encode_args(self, password: str, salt: str, /):
        if not password:
            raise ValueError() from None
        if not salt or self.separator in salt:
            raise ValueError() from None

    @abstractmethod
    def encode(
        self,
        password: str,
        /,
        *,
        salt: str | None = None,
        iterations: int | None = None,
    ) -> str: ...

    @abstractmethod
    def decode(self, encoded, /) -> DecodedPassword: ...


class HashMismatch(HasherBaseException):
    """Hash Mismatch"""


class PasswordHasherPBKDF2(PasswordHasherBase):
    algorithm: str = "pbkdf2_sha256"
    iterations: int = 600000
    digest = hashlib.sha256

    def encode(
        self,
        password: str,
        /,
        *,
        salt: str | None = None,
        iterations: int | None = None,
    ) -> str:
        if salt is None:
            salt = self.salt()
        self._check_encode_args(password, salt)

        if iterations is None:
            iterations = self.iterations

        hash_ = self.pbkdf2(
            password.encode(),
            salt.encode(),
            iterations,
            digest=getattr(self, "digest"),  # noqa: B009 Dirty hack, all questions to mypy.
        )
        hash_ = base64.b64encode(hash_).decode("ascii").strip()
        return f"{self.algorithm}{self.separator}{iterations}{self.separator}{salt}{self.separator}{hash_}"

    def decode(self, encoded, /) -> DecodedPassword:
        algorithm, iterations, salt, hash_ = encoded.split(self.separator, 3)
        if algorithm != self.algorithm:
            logger.exception("Algorithm mismatch")
            raise HashMismatch() from None
        return DecodedPassword(
            algorithm=algorithm,
            hash=hash_,
            iterations=iterations,
            salt=salt,
        )

    def verify(self, password: str, encoded: str, /) -> bool:
        decoded_password: DecodedPassword = self.decode(encoded)
        encoded_: str = self.encode(
            password,
            salt=decoded_password.salt,
            iterations=decoded_password.iterations,
        )
        return self.compare(encoded.encode(), encoded_.encode())


hasher = PasswordHasherPBKDF2()
