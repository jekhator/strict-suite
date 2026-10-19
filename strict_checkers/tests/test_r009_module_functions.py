"""Tests for R009: module-level functions without a recorded reason."""

from strict_config import constants as const
from strict_config._config import Config
from strict_linter import DtoStrictLinter
from strict_rules import RuleSeverity


class TestR009ModuleLevelFunctions:
    """Test suite for R009 module-level function detection."""

    def test_r009_reports_untagged_module_function_as_info(self, fixture_dir):
        """R009 flags untagged module-level functions at INFO severity."""
        linter = DtoStrictLinter(Config())
        violations = linter.lint_file(
            fixture_dir / "bad" / "r009_module_function_outside_entry_point.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 2, (
            f"Expected 2 R009 violations (process_data, calculate_sum), "
            f"got {len(r009_violations)}"
        )
        assert all(v.severity == RuleSeverity.INFO for v in r009_violations)

    def test_r009_allows_entry_points(self, fixture_dir):
        """R009 allows main, handle_*, and related entry points."""
        linter = DtoStrictLinter(Config())
        violations = linter.lint_file(
            fixture_dir / "good" / "r009_allowed_entry_points.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 0, (
            f"Expected 0 R009 violations (all are allowed entry points), "
            f"got {len(r009_violations)}: {r009_violations}"
        )

    def test_r009_exempts_test_files(self, fixture_dir):
        """R009 does not flag functions in test files."""
        linter = DtoStrictLinter(Config())
        violations = linter.lint_file(
            fixture_dir / "good" / "test_r008_good_test_class.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 0, "R009 should not flag functions in test files"

    def test_r009_exempts_pytest_fixtures(self, fixture_dir):
        """R009 does not flag pytest fixtures."""
        linter = DtoStrictLinter(Config())
        violations = linter.lint_file(fixture_dir / "bad" / "test_r007_bad_fixtures.py")
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 0, "R009 should exempt pytest fixtures"

    def test_r009_exempts_decorators_hooks_and_recorded_reasons(self, fixture_dir):
        """R009 exempts decorated functions, dunder and pytest hooks, and tagged functions."""
        linter = DtoStrictLinter(Config())
        violations = linter.lint_file(fixture_dir / "good" / "r009_exempt_shapes.py")
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert r009_violations == [], (
            f"Expected every module-level shape in the fixture to be exempt, "
            f"got {r009_violations}"
        )

    def test_r009_message_names_entry_points_and_tag(self, fixture_dir):
        """R009 message lists the entry points and the recorded-reason tag."""
        linter = DtoStrictLinter(Config())
        violations = linter.lint_file(
            fixture_dir / "bad" / "r009_module_function_outside_entry_point.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) > 0
        message = r009_violations[0].message
        assert "main" in message, "Message should mention 'main' entry point"
        assert "handle_" in message, "Message should mention 'handle_*' pattern"
        assert "# module-level:" in message, "Message should name the recorded-reason tag"

    def test_r009_default_tag_is_recognized_out_of_the_box(self):
        """The module-level tag is in the default exception tags."""
        assert const.TAG_MODULE_LEVEL in Config().exception_tags

    def test_r009_default_tag_is_the_colon_form(self):
        """The default tag is the written form with a colon, so prose cannot satisfy it."""
        assert const.TAG_MODULE_LEVEL == "module-level:"

    def test_r009_prose_docstring_does_not_exempt(self, fixture_dir):
        """A first docstring line that only mentions module-level as prose still gets an R009 finding."""
        linter = DtoStrictLinter(Config())
        violations = linter.lint_file(
            fixture_dir / "bad" / "r009_prose_docstring_not_a_tag.py"
        )
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 1, (
            f"Expected 1 R009 violation for the prose-only docstring, "
            f"got {len(r009_violations)}"
        )
        assert "strip_prefix" in r009_violations[0].message

    def test_r009_default_run_exits_zero(self, fixture_dir):
        """With default severity, R009 findings are advisory and the run exits zero."""
        linter = DtoStrictLinter(Config())
        violations = linter.lint_path(
            fixture_dir / "bad" / "r009_module_function_outside_entry_point.py"
        )

        assert len(violations) == 2
        assert linter.get_exit_code(violations) == const.EXIT_CODE_SUCCESS

    def test_r009_severity_override_to_high_blocks(self, fixture_dir):
        """Setting R009 to HIGH restores a blocking exit code."""
        config = Config(severity_overrides={"R009": "HIGH"})
        linter = DtoStrictLinter(config)
        violations = linter.lint_path(
            fixture_dir / "bad" / "r009_module_function_outside_entry_point.py"
        )

        assert all(v.severity == RuleSeverity.HIGH for v in violations)
        assert linter.get_exit_code(violations) == const.EXIT_CODE_HIGH_VIOLATION
