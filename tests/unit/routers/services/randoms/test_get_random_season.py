from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import NoResultFound

from futuramaapi.repositories.models import SeasonModel
from futuramaapi.routers.services import NotFoundError
from futuramaapi.routers.services.randoms.get_random_season import GetRandomSeasonService


class TestGetRandomSeasonService:
    @pytest.mark.asyncio
    async def test_get_random_season_service_success(self, season: SeasonModel, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.return_value = season
        mock_session_manager.execute.return_value = mock_result

        service = GetRandomSeasonService()

        # Act
        result = await service()

        # Assert
        assert result.id == season.id
        assert result.episodes[0].id == season.episodes[0].id

    @pytest.mark.asyncio
    async def test_get_random_season_service_not_found(self, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.side_effect = NoResultFound
        mock_session_manager.execute.return_value = mock_result

        service = GetRandomSeasonService()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service()
