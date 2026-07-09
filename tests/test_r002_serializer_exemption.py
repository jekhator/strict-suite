"""Tests for R002 exemption: dict literals in to_* methods of dataclasses."""

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
        service_paths=[
            "*/**/*.py",
            "tests/fixtures/**/*.py",
        ],  # Check all files for testing
        dto_paths=["**/dtos.py"],
    )


def test_r002_exempt_serializer_methods(fixture_dir, config):
    """Good: dict literals in to_* methods of dataclasses are exempt."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "good" / "r002_good_serializer.py")
    r002_violations = [v for v in violations if v.rule_id == "R002"]
    assert len(r002_violations) == 0, (
        "to_* methods in dataclasses should be exempt from R002"
    )


def test_r002_flags_non_serializer_in_dataclass(fixture_dir, config):
    """Bad: dict literals in non-to_* methods of dataclasses are still flagged."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "bad" / "r002_bad_non_serializer.py")
    r002_violations = [v for v in violations if v.rule_id == "R002"]
    # get_metadata() should be flagged (non-to_* in dataclass)
    # to_dict() in PlainClass should be flagged (non-dataclass)
    assert len(r002_violations) >= 1, (
        "get_metadata() with inline dict should be flagged"
    )
    # Verify at least one violation mentions the line or shows the dict counts
    assert any("keys" in v.message for v in r002_violations), (
        "Violation should mention dict keys"
    )
