from json import dumps
from typing import Dict

import pytest

from app.core.settings import parse


class TestParse:
    def test_parse_should_raise_not_implemented_error_when_unsupported_cast_type_provided(
        self
    ):
        with pytest.raises(NotImplementedError):
            parse(tuple, "", ",")

    def test_parse_should_return_str_when_str_requested_and_value_is_str(self):
        assert parse(str, "true", ",") == "true"

    def test_parse_should_return_psql_async_url_when_db_url_and_async_requested_and_sync_url_provided(
        self
    ):
        result = parse(
            str,
            "postgresql://user:password@host/db_name",
            ",",
            async_=True,
            db_url=True,
        )

        assert result == "postgresql+asyncpg://user:password@host/db_name"

    def test_parse_should_return_postgresql_protocol_when_db_url_requested_and_postgres_protocol_provided(
        self
    ):
        result = parse(
            str,
            "postgres://user:password@host/db_name",
            ",",
            db_url=True,
        )

        assert result == "postgresql://user:password@host/db_name"

    def test_parse_should_return_bool_true_when_bool_requested_and_value_is_str_true(
        self
    ):
        assert parse(bool, "true", ",") is True

    def test_parse_should_return_bool_true_when_bool_requested_and_value_is_str_false(
        self
    ):
        assert parse(bool, "false", ",") is False

    def test_parse_should_return_list_when_list_requested_and_value_is_str_separated_by_comma(
        self
    ):
        initial_setting = "host1,host2,host3"
        result = ["host1", "host2", "host3"]

        assert parse(list, initial_setting, ",") == result

    def test_parse_should_return_list_when_list_requested_and_value_is_str_separated_by_pipe(
        self
    ):
        initial_setting = "host1|host2|host3"
        result = ["host1", "host2", "host3"]

        assert parse(list, initial_setting, "|") == result

    def test_parse_should_raise_runtime_error_when_dict_requested_and_value_is_not_dict(
        self
    ):
        with pytest.raises(RuntimeError):
            parse(dict, "NOT A DICTIONARY", ",")

    def test_parse_should_return_valid_dict_when_dict_requested_and_value_is_valid_dict(
        self
    ):
        orig_dict = dict(test_key="test_val")
        dict_: Dict = parse(Dict, dumps(orig_dict), ",")

        assert dict_ == orig_dict
