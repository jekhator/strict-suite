"""Bad: pytest fixture using @fixture() call form in test file."""

import pytest


def test_something():
    """A test function."""
    pass


@pytest.fixture(scope="function")
def my_resource():
    """A fixture defined outside conftest.py with fixture() call."""
    return "resource"
