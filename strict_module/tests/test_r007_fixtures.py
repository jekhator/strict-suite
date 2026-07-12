"""Tests for R007: pytest fixtures defined outside conftest.py."""

import tempfile
from pathlib import Path

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestR007Fixtures:
    """Test suite for related functionality."""

    def test_r007_bad_fixture_in_test_file(self, fixture_dir):
        """Bad: pytest fixture defined in non-conftest test file."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "test_r007_bad_fixtures.py")
        r007_violations = [v for v in violations if v.rule_id == "R007"]
        assert len(r007_violations) >= 1
        assert any("fixture" in v.message.lower() for v in r007_violations)
        assert any("conftest" in v.message.lower() for v in r007_violations)

    def test_r007_good_fixture_defined_in_conftest(self, fixture_dir):
        """Good: fixtures properly defined in conftest.py are not flagged.

        This test verifies that test files with conftest.py don't trigger R007.
        The conftest.py file itself can contain fixtures.
        """
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        # Create a temporary conftest.py to test
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
