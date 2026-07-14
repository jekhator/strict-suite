"""Tests for R009: Module-level functions outside allowed entry points."""

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestR009ModuleLevelFunctions:
    """Test suite for R009 module-level function detection."""

    def test_r009_detects_module_level_function(self, fixture_dir):
        """R009 should flag module-level functions in service paths."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r009_module_function_outside_entry_point.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 2, (
            f"Expected 2 R009 violations (process_data, calculate_sum), "
            f"got {len(r009_violations)}"
        )

    def test_r009_allows_entry_points(self, fixture_dir):
        """R009 should allow main, handle_*, and related entry points."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "good" / "r009_allowed_entry_points.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 0, (
            f"Expected 0 R009 violations (all are allowed entry points), "
            f"got {len(r009_violations)}: {r009_violations}"
        )

    def test_r009_exempts_test_files(self, fixture_dir):
        """R009 should not flag functions in test files."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "good" / "test_r008_good_test_class.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 0, "R009 should not flag functions in test files"

    def test_r009_exempts_fixtures(self, fixture_dir):
        """R009 should not flag pytest fixtures."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "test_r007_bad_fixtures.py")
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 0, "R009 should exempt pytest fixtures"

    def test_r009_message_suggests_allowed_entry_points(self, fixture_dir):
        """R009 violation message should list allowed entry points."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r009_module_function_outside_entry_point.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) > 0
        message = r009_violations[0].message
        assert "main" in message, "Message should mention 'main' entry point"
        assert "handle_" in message, "Message should mention 'handle_*' pattern"
