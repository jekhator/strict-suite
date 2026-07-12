"""Tests for R004: Module-level functions without exception tags."""

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
        exception_tags=["facade - celery schedule", "FRAMEWORK"],
    )


def test_r004_good_with_tags(fixture_dir, config):
    """Good: module-level functions with exception tags."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "good" / "r004_good_facade.py")
    r004_violations = [v for v in violations if v.rule_id == "R004"]
    assert len(r004_violations) == 0


def test_r004_bad_no_tags(fixture_dir, config):
    """Bad: module-level functions without tags."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "bad" / "r004_bad_facade.py")
    r004_violations = [v for v in violations if v.rule_id == "R004"]
    assert len(r004_violations) >= 2
