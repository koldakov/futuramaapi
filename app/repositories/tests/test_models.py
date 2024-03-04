from app.repositories.models import to_camel


class TestModelUtils:
    def test_to_camel_should_return_snake_case_when_lower_case_text_has_one_underline(self):
        assert to_camel("snake_case") == "snakeCase"

    def test_to_camel_should_return_snake_case_when_lower_case_text_has_two_underlines(self):
        assert to_camel("snake_case_snake") == "snakeCaseSnake"

    def test_to_camel_should_return_snake_case_when_upper_case_text_has_one_underline(self):
        assert to_camel("SNAKE_CASE") == "snakeCase"
