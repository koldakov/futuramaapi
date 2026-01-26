from unittest.mock import MagicMock

import pytest
from faker import Faker
from fastapi import HTTPException
from fastapi_storages import FileSystemStorage, StorageImage
from pydantic import HttpUrl
from sqlalchemy.exc import NoResultFound

from futuramaapi.core import settings
from futuramaapi.repositories import INT32
from futuramaapi.repositories.models import CharacterModel
from futuramaapi.routers.services.characters.get_character import GetCharacterService


class TestGetCharacterService:
    @pytest.mark.asyncio
    async def test_get_character_service_success(self, character: CharacterModel, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.return_value = character
        mock_session_manager.execute.return_value = mock_result

        service = GetCharacterService(pk=character.id)

        # Act
        result = await service()

        # Assert
        assert result.id == character.id
        assert result.name == character.name

    @pytest.mark.asyncio
    async def test_get_character_service_success_image_is_none(self, character: CharacterModel, mock_session_manager):
        # Arrange
        character.image = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.one.return_value = character
        mock_session_manager.execute.return_value = mock_result

        service = GetCharacterService(pk=character.id)

        # Act
        result = await service()

        # Assert
        assert result.id == character.id
        assert result.name == character.name
        assert result.image is None

    @pytest.mark.asyncio
    async def test_get_character_service_success_image_is_storage_image(
        self,
        faker: Faker,
        character: CharacterModel,
        mock_session_manager,
    ):
        # Arrange
        image_name: str = faker.word()
        character.image = StorageImage(
            name=image_name,
            storage=FileSystemStorage(path=settings.project_root / settings.static),
            width=faker.random_int(),
            height=faker.random_int(),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.one.return_value = character
        mock_session_manager.execute.return_value = mock_result

        service = GetCharacterService(pk=character.id)

        # Act
        result = await service()

        # Assert
        assert result.id == character.id
        assert result.name == character.name
        assert result.image == HttpUrl(f"https://localhost/static/{image_name}")

    @pytest.mark.asyncio
    async def test_get_character_service_not_found(self, faker: Faker, mock_session_manager):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.one.side_effect = NoResultFound
        mock_session_manager.execute.return_value = mock_result

        service = GetCharacterService(
            pk=faker.random_int(
                min=1,
                max=INT32,
            ),
        )

        # Act & Assert
        with pytest.raises(HTTPException):
            await service()
