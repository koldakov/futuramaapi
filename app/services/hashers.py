import base64
import hashlib
import math
import secrets

from pydantic import BaseModel

RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def pbkdf2(
    password: bytes,
    salt: bytes,
    iterations: int,
    /,
    *,
    dk_len: int = 0,
    digest=None,
):
    if digest is None:
        digest = hashlib.sha256
    dk_len = dk_len or None
    return hashlib.pbkdf2_hmac(digest().name, password, salt, iterations, dk_len)


def compare(
    val1: bytes,
    val2: bytes,
    /,
) -> bool:
    return secrets.compare_digest(val1, val2)


def get_random_string(
    length: int,
    /,
    *,
    allowed_chars=RANDOM_STRING_CHARS,
):
    return "".join(secrets.choice(allowed_chars) for i in range(length))


class DecodedPassword(BaseModel):
    algorithm: str
    hash: str
    iterations: int
    salt: str


class PasswordHasherBase:
    algorithm = None
    library = None
    salt_entropy = 128
    separator = "."

    def salt(self) -> str:
        count = math.ceil(self.salt_entropy / math.log2(len(RANDOM_STRING_CHARS)))
        return get_random_string(count, allowed_chars=RANDOM_STRING_CHARS)

    def verify(self, password, encoded, /) -> bool:
        raise NotImplementedError()

    def _check_encode_args(self, password: str, salt: str, /):
        if not password:
            raise ValueError() from None
        if not salt or self.separator in salt:
            raise ValueError() from None

    def encode(self, password, salt, /) -> str:
        raise NotImplementedError()

    def decode(self, encoded, /) -> DecodedPassword:
        raise NotImplementedError()


class PasswordHasherPBKDF2(PasswordHasherBase):
    algorithm: str = "pbkdf2_sha256"
    iterations: int = 600000
    digest = hashlib.sha256

    def encode(
        self,
        password: str,
        /,
        *,
        salt: str = None,
        iterations: int = None,
    ) -> str:
        if not salt:
            salt = self.salt()
        self._check_encode_args(password, salt)
        iterations = iterations or self.iterations
        hash_ = pbkdf2(password.encode(), salt.encode(), iterations, digest=self.digest)
        hash_ = base64.b64encode(hash_).decode("ascii").strip()
        return f"{self.algorithm}{self.separator}{iterations}{self.separator}{salt}{self.separator}{hash_}"

    def decode(self, encoded, /) -> DecodedPassword:
        algorithm, iterations, salt, hash_ = encoded.split(self.separator, 3)
        assert algorithm == self.algorithm
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
        return compare(encoded.encode(), encoded_.encode())


hasher = PasswordHasherPBKDF2()
