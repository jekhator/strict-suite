"""Tests for R003: Dataclass missing frozen+slots+repr=False trio."""

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
        service_paths=["**/services/*.py"],
        dto_paths=["**/*.py"],  # Check all files for DTO testing
        r003_mode="legacy",  # Use legacy mode for backward compat with v0.1 tests
    )


def test_r003_good_complete_trio(fixture_dir, config):
    """Good: dataclass with frozen=True, slots=True, repr=False."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "good" / "r003_good_dataclass.py")
    r003_violations = [v for v in violations if v.rule_id == "R003"]
    assert len(r003_violations) == 0


def test_r003_bad_missing_parameters(fixture_dir, config):
    """Bad: dataclass missing required parameters."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "bad" / "r003_bad_dataclass.py")
    r003_violations = [v for v in violations if v.rule_id == "R003"]
    assert len(r003_violations) >= 2
