"""Tests for R002: Inline dict literals with 3+ string keys."""

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
        service_paths=["**/*.py"],  # Check all files for testing
        dto_paths=["**/dtos.py"],
    )


def test_r002_good_few_keys(fixture_dir, config):
    """Good: dict literals with <3 keys."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "good" / "r002_good_dict.py")
    r002_violations = [v for v in violations if v.rule_id == "R002"]
    assert len(r002_violations) == 0


def test_r002_bad_inline_dict(fixture_dir, config):
    """Bad: inline dict literals with 3+ keys."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "bad" / "r002_bad_inline.py")
    r002_violations = [v for v in violations if v.rule_id == "R002"]
    assert len(r002_violations) >= 1
