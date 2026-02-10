from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import NoResultFound

from futuramaapi.db.models import CharacterModel
from futuramaapi.routers.services import NotFoundError
from futuramaapi.routers.services.randoms.get_random_character import GetRandomCharacterService


class TestGetRandomCharacterService:
    @pytest.mark.asyncio
    async def test_get_random_character_service_success(self, character: CharacterModel, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.return_value = character
        mock_session_manager.execute.return_value = mock_result

        service = GetRandomCharacterService()

        # Act
        result = await service()

        # Assert
        assert result.id == character.id
        assert result.name == character.name

    @pytest.mark.asyncio
    async def test_get_random_character_service_not_found(self, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.side_effect = NoResultFound
        mock_session_manager.execute.return_value = mock_result

        service = GetRandomCharacterService()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service()
