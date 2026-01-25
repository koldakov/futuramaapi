from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from faker import Faker

from futuramaapi.repositories import INT32
from futuramaapi.repositories.models import CharacterModel


@pytest.fixture
def character(faker: Faker):
    return CharacterModel(
        id=faker.random_int(
            min=1,
            max=INT32,
        ),
        name=faker.name(),
        gender=CharacterModel.CharacterGender.MALE,
        status=CharacterModel.CharacterStatus.ALIVE,
        species=CharacterModel.CharacterSpecies.HUMAN,
        created_at=datetime.now(UTC),
        image=faker.image_url(),
    )


@pytest.fixture
def mock_session_manager(request):
    mock_context = AsyncMock()
    mock_session = AsyncMock()
    mock_context.__aenter__.return_value = mock_session

    patcher = patch(
        "futuramaapi.routers.services._base.session_manager.session",
        return_value=mock_context,
    )
    patcher.start()
    request.addfinalizer(patcher.stop)

    return mock_session
