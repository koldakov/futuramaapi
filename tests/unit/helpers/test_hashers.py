from futuramaapi.helpers.hashers import hasher


class TestHasher:
    def test_verify(self):
        password: str = "123"  # noqa: S105
        decoded: str = hasher.encode(password)

        assert hasher.verify(password, decoded)
