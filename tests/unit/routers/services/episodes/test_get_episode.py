from unittest.mock import MagicMock

import pytest
from faker import Faker
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from futuramaapi.repositories import INT32
from futuramaapi.repositories.models import EpisodeModel
from futuramaapi.routers.services.episodes.get_episode import GetEpisodeService


class TestGetEpisodeService:
    @pytest.mark.asyncio
    async def test_get_episode_service_success(self, episode: EpisodeModel, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.return_value = episode
        mock_session_manager.execute.return_value = mock_result

        service = GetEpisodeService(pk=episode.id)

        # Act
        result = await service()

        # Assert
        assert result.id == episode.id
        assert result.name == episode.name
        assert result.broadcast_code == f"S{episode.season.id:02d}E{episode.broadcast_number:02d}"

    @pytest.mark.asyncio
    async def test_get_episode_service_not_found(self, faker: Faker, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.side_effect = NoResultFound
        mock_session_manager.execute.return_value = mock_result

        service = GetEpisodeService(
            pk=faker.random_int(
                min=1,
                max=INT32,
            ),
        )

        # Act & Assert
        with pytest.raises(HTTPException):
            await service()
