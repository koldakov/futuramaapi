from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from futuramaapi.routers.services.seasons.list_seasons import ListSeasonsService


@pytest.fixture
def mock_apaginate(request):
    patcher = patch(
        "futuramaapi.routers.services.seasons.list_seasons.apaginate",
        new_callable=AsyncMock,
    )
    mocked = patcher.start()
    request.addfinalizer(patcher.stop)
    return mocked


class TestListSeasonsService:
    @pytest.mark.asyncio
    async def test_list_seasons_success(
        self,
        mock_session_manager,
        mock_apaginate,
    ):
        # Arrange
        page = MagicMock()
        mock_apaginate.return_value = page

        service = ListSeasonsService()

        # Act
        result = await service()

        # Assert
        assert result is page
        mock_apaginate.assert_called_once()

        args, _ = mock_apaginate.call_args
        assert args[0] is mock_session_manager
