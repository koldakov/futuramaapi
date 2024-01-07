import os

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(args, early_config, parser):
    with open(".env.template") as file:
        data = file.read()

    for line in data.split():
        if line.startswith("#"):
            continue

        key, value = line.split()[0].split("=", 1)
        os.environ[key] = value
