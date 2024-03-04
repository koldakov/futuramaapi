import pytest

from app.graph_ql.schemas import LimitViolation, validate_limit


class TestLimitValidation:
    def test_validate_limit_should_raise_limit_violation_when_limit_less_then_min_allowed_value(self):
        with pytest.raises(LimitViolation):
            validate_limit(0, 1, 3)

    def test_validate_limit_should_raise_limit_violation_when_limit_more_then_max_allowed_value(self):
        with pytest.raises(LimitViolation):
            validate_limit(4, 1, 3)

    def test_validate_limit_should_return_none_when_limit_more_then_min_value_and_less_then_max_value(self):
        assert validate_limit(2, 1, 3) is None
