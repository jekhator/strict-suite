"""Tests for R004: Module-level functions without exception tags."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR004ModuleFacade:
    """Test suite for related functionality."""

    def test_r004_good_with_tags(self, fixture_dir):
        """Good: module-level functions with exception tags."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            exception_tags=["facade - celery schedule", "FRAMEWORK"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "good" / "r004_good_facade.py")
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert len(r004_violations) == 0

    def test_r004_bad_no_tags(self, fixture_dir):
        """Bad: module-level functions without tags."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            exception_tags=["facade - celery schedule", "FRAMEWORK"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r004_bad_facade.py")
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert len(r004_violations) >= 2
