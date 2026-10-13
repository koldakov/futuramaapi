from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from futuramaapi.routers.services.episodes.list_episodes import ListEpisodesService


@pytest.fixture
def mock_apaginate(request):
    patcher = patch(
        "futuramaapi.routers.services.episodes.list_episodes.apaginate",
        new_callable=AsyncMock,
    )
    mocked = patcher.start()
    request.addfinalizer(patcher.stop)
    return mocked


class TestListEpisodesService:
    @pytest.mark.asyncio
    async def test_list_episodes_success(
        self,
        mock_session_manager,
        mock_apaginate,
    ):
        # Arrange
        page = MagicMock()
        mock_apaginate.return_value = page

        service = ListEpisodesService()

        # Act
        result = await service()

        # Assert
        assert result is page
        mock_apaginate.assert_called_once()

        args, _ = mock_apaginate.call_args
        assert args[0] is mock_session_manager
