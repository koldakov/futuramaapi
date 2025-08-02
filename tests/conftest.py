import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def ensure_env(monkeypatch):
    load_dotenv(".env", override=True)
