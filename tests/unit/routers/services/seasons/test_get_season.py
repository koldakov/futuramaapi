from unittest.mock import MagicMock

import pytest
from faker import Faker
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from futuramaapi.repositories import INT32
from futuramaapi.repositories.models import SeasonModel
from futuramaapi.routers.services.seasons.get_season import GetSeasonService


class TestGetSeasonService:
    @pytest.mark.asyncio
    async def test_get_season_service_success(self, season: SeasonModel, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.return_value = season
        mock_session_manager.execute.return_value = mock_result

        service = GetSeasonService(pk=season.id)

        # Act
        result = await service()

        # Assert
        assert result.id == season.id
        assert result.episodes[0].id == season.episodes[0].id

    @pytest.mark.asyncio
    async def test_get_season_service_not_found(self, faker: Faker, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.side_effect = NoResultFound
        mock_session_manager.execute.return_value = mock_result

        service = GetSeasonService(
            pk=faker.random_int(
                min=1,
                max=INT32,
            ),
        )

        # Act & Assert
        with pytest.raises(HTTPException):
            await service()
