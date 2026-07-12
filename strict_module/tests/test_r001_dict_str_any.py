"""Tests for R001: Dict[str, Any] in service signatures."""

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


def test_r001_good_no_dict_str_any(fixture_dir, config):
    """Good: no Dict[str, Any] in signatures."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "good" / "r001_good_basic.py")
    r001_violations = [v for v in violations if v.rule_id == "R001"]
    assert len(r001_violations) == 0


def test_r001_bad_param_dict_str_any(fixture_dir, config):
    """Bad: Dict[str, Any] in parameter."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "bad" / "r001_bad_param.py")
    r001_violations = [v for v in violations if v.rule_id == "R001"]
    assert len(r001_violations) >= 1
    assert any("Dict[str, Any]" in v.message for v in r001_violations)


def test_r001_bad_return_dict_str_any(fixture_dir, config):
    """Bad: Dict[str, Any] in return type."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "bad" / "r001_bad_return.py")
    r001_violations = [v for v in violations if v.rule_id == "R001"]
    assert len(r001_violations) >= 1
