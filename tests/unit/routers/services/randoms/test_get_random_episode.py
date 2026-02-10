from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import NoResultFound

from futuramaapi.db.models import EpisodeModel
from futuramaapi.routers.services import NotFoundError
from futuramaapi.routers.services.randoms.get_random_episode import GetRandomEpisodeService


class TestGetRandomEpisodeService:
    @pytest.mark.asyncio
    async def test_get_random_episode_service_success(self, episode: EpisodeModel, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.return_value = episode
        mock_session_manager.execute.return_value = mock_result

        service = GetRandomEpisodeService()

        # Act
        result = await service()

        # Assert
        assert result.id == episode.id
        assert result.name == episode.name

    @pytest.mark.asyncio
    async def test_get_random_episode_service_not_found(self, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.side_effect = NoResultFound
        mock_session_manager.execute.return_value = mock_result

        service = GetRandomEpisodeService()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service()
