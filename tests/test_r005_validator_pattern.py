"""Tests for R005: Validator not using DTO.from_dict() pattern."""

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


def test_r005_good_with_dto_pattern(fixture_dir, config):
    """Good: validators using DTO.from_dict() or raising ValidationError."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "good" / "r005_good_validator.py")
    r005_violations = [v for v in violations if v.rule_id == "R005"]
    assert len(r005_violations) == 0


def test_r005_bad_loose_validation(fixture_dir, config):
    """Bad: validators not using proper DTO pattern."""
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(fixture_dir / "bad" / "r005_bad_validator.py")
    r005_violations = [v for v in violations if v.rule_id == "R005"]
    assert len(r005_violations) >= 2
