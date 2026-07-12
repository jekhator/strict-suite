"""Tests for R008: bare module-level test functions."""

from pathlib import Path

import pytest

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


def test_r008_bad_bare_test_functions(fixture_dir, config):
    """Bad: test functions defined at module level."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(
        fixture_dir / "bad" / "test_r008_bad_bare_test_functions.py"
    )
    r008_violations = [v for v in violations if v.rule_id == "R008"]
    # Should find at least 3 bare test functions
    assert len(r008_violations) >= 3
    assert all("module-level" in v.message.lower() for v in r008_violations)
    assert any("test_addition" in v.message for v in r008_violations)


def test_r008_good_test_functions_in_classes(fixture_dir, config):
    """Good: test functions properly organized in classes."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "good" / "test_r008_good_test_class.py")
    r008_violations = [v for v in violations if v.rule_id == "R008"]
    assert len(r008_violations) == 0
