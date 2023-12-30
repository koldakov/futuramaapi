from app.repositories.models import Character


class TestBase:
    character = Character(id=1)

    def test_to_dict_should_return_dict_with_id_when_id_provided(self):
        assert self.character.to_dict() == {"id": 1}

    def test_to_dict_should_return_empty_dict_when_id_provided_and_id_excluded(self):
        assert self.character.to_dict(exclude=["id"]) == {}

    def test_to_dict_should_not_return__sa_instance_state_in_dict_when_requested(self):
        assert "_sa_instance_state" not in self.character.to_dict()
