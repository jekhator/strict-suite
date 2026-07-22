"""Tests for R005: Validator not using DTO.from_dict() pattern."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR005ValidatorPattern:
    """Test suite for related functionality."""

    def test_r005_good_with_dto_pattern(self, fixture_dir):
        """Good: validators using DTO.from_dict() or raising ValidationError."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "good" / "r005_good_validator.py")
        r005_violations = [v for v in violations if v.rule_id == "R005"]
        assert len(r005_violations) == 0

    def test_r005_bad_loose_validation(self, fixture_dir):
        """Bad: validators not using proper DTO pattern."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r005_bad_validator.py")
        r005_violations = [v for v in violations if v.rule_id == "R005"]
        assert len(r005_violations) >= 2
