"""Bad: pytest fixtures defined in non-conftest file."""

import pytest


@pytest.fixture
def sample_data():
    """Fixture that should be in conftest.py."""
    return {"key": "value"}


def test_using_fixture(sample_data):
    """Test that uses the fixture."""
    assert sample_data["key"] == "value"
