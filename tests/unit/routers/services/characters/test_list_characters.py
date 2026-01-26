from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from faker import Faker

from futuramaapi.routers.services.characters.list_characters import ListCharactersService


@pytest.fixture
def mock_paginate(request):
    patcher = patch(
        "futuramaapi.routers.services.characters.list_characters.paginate",
        new_callable=AsyncMock,
    )
    mocked = patcher.start()
    request.addfinalizer(patcher.stop)
    return mocked


class TestListCharactersService:
    @pytest.mark.asyncio
    async def test_list_characters_success(
        self,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        page = MagicMock()
        mock_paginate.return_value = page

        service = ListCharactersService(
            gender=None,
            character_status=None,
            species=None,
            query=None,
        )

        # Act
        result = await service()

        # Assert
        assert result is page
        mock_paginate.assert_called_once()

        args, _ = mock_paginate.call_args
        assert args[0] is mock_session_manager

    @pytest.mark.asyncio
    async def test_list_characters_gender_negation(
        self,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        mock_paginate.return_value = MagicMock()

        service = ListCharactersService(
            gender="!male",
            character_status=None,
            species=None,
            query=None,
        )

        # Act
        await service()

        # Assert
        mock_paginate.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_characters_gender_positive(
        self,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        mock_paginate.return_value = MagicMock()

        service = ListCharactersService(
            gender="male",
            character_status=None,
            species=None,
            query=None,
        )

        # Act
        await service()

        # Assert
        mock_paginate.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_characters_status_positive(
        self,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        mock_paginate.return_value = MagicMock()

        service = ListCharactersService(
            gender=None,
            character_status="alive",
            species=None,
            query=None,
        )

        # Act
        await service()

        # Assert
        mock_paginate.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_characters_status_negation(
        self,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        mock_paginate.return_value = MagicMock()

        service = ListCharactersService(
            gender=None,
            character_status="!alive",
            species=None,
            query=None,
        )

        # Act
        await service()

        # Assert
        mock_paginate.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_characters_species_positive(
        self,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        mock_paginate.return_value = MagicMock()

        service = ListCharactersService(
            gender=None,
            character_status=None,
            species="human",
            query=None,
        )

        # Act
        await service()

        # Assert
        mock_paginate.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_characters_species_negation(
        self,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        mock_paginate.return_value = MagicMock()

        service = ListCharactersService(
            gender=None,
            character_status=None,
            species="!human",
            query=None,
        )

        # Act
        await service()

        # Assert
        mock_paginate.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_characters_query_filter(
        self,
        faker: Faker,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        mock_paginate.return_value = MagicMock()

        service = ListCharactersService(
            gender=None,
            character_status=None,
            species=None,
            query=faker.word(),
        )

        # Act
        await service()

        # Assert
        mock_paginate.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_characters_order_desc(
        self,
        mock_session_manager,
        mock_paginate,
    ):
        # Arrange
        mock_paginate.return_value = MagicMock()

        service = ListCharactersService(
            order_by="id",
            direction="desc",
            gender=None,
            character_status=None,
            species=None,
            query=None,
        )

        # Act
        await service()

        # Assert
        mock_paginate.assert_called_once()
