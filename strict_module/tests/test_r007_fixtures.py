"""Tests for R007: pytest fixtures defined outside conftest.py."""

import pytest
from pathlib import Path
from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


@pytest.fixture
def fixture_dir():
    """Get fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def config():
    """Create a test config."""
    return Config(
        service_paths=["**/*.py"],
        dto_paths=["**/dtos.py"],
    )


def test_r007_bad_fixture_in_test_file(fixture_dir, config):
    """Bad: pytest fixture defined in non-conftest test file."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "bad" / "test_r007_bad_fixtures.py")
    r007_violations = [v for v in violations if v.rule_id == "R007"]
    assert len(r007_violations) >= 1
    assert any("fixture" in v.message.lower() for v in r007_violations)
    assert any("conftest" in v.message.lower() for v in r007_violations)


def test_r007_good_fixture_defined_in_conftest(fixture_dir, config):
    """Good: fixtures properly defined in conftest.py are not flagged.

    This test verifies that test files with conftest.py don't trigger R007.
    The conftest.py file itself can contain fixtures.
    """
    # Create a temporary conftest.py to test
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        conftest_path = Path(tmpdir) / "conftest.py"
        conftest_path.write_text("""
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}
""")
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(conftest_path)
        r007_violations = [v for v in violations if v.rule_id == "R007"]
        # conftest.py should not trigger R007
        assert len(r007_violations) == 0
