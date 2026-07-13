"""Bad: pytest fixture using bare @fixture decorator in test file."""

from pytest import fixture


def test_something():
    """A test function."""
    pass


@fixture
def my_resource():
    """A fixture defined outside conftest.py with bare decorator."""
    return "resource"
