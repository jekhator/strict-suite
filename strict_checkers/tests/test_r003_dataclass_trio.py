"""Tests for R003: Dataclass missing frozen+slots+repr=False trio."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR003DataclassTrio:
    """Test suite for related functionality."""

    def test_r003_good_complete_trio(self, fixture_dir):
        """Good: dataclass with frozen=True, slots=True, repr=False."""
        config = Config(
            service_paths=["**/services/*.py"],
            dto_paths=["**/*.py"],
            r003_mode="legacy",
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "good" / "r003_good_dataclass.py")
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) == 0

    def test_r003_bad_missing_parameters(self, fixture_dir):
        """Bad: dataclass missing required parameters."""
        config = Config(
            service_paths=["**/services/*.py"],
            dto_paths=["**/*.py"],
            r003_mode="legacy",
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r003_bad_dataclass.py")
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) >= 2
