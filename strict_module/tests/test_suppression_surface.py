"""Tests for suppression surface fixes: severity overrides, INFO level, noqa rule codes."""

import ast
import tempfile
from pathlib import Path

from strict_module.config import Config
from strict_module.inspection import AnnotationInspector
from strict_module.linter import DtoStrictLinter
from strict_module.rules.rules_objects import RuleSeverity, Violation


class TestSeverityOverridesFix:
    """Test Fix A: severity_overrides now apply correctly."""

    def test_severity_override_applied_to_r011(self):
        """Severity override for R011 should actually modify the violation."""
        config = Config(severity_overrides={"R011": "LOW"})

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text('raise ValueError("error message")')

            linter = DtoStrictLinter(config)
            result = linter.lint_path(bad_file)

            for v in result:
                if v.rule_id == "R011":
                    assert v.severity == RuleSeverity.LOW, (
                        "Override not applied: R011 should have LOW severity"
                    )

    def test_severity_override_not_applied_without_override_config(self):
        """Without override, R011 should keep original severity (HIGH)."""
        config = Config()

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text('raise ValueError("error message")')

            linter = DtoStrictLinter(config)
            result = linter.lint_path(bad_file)

            for v in result:
                if v.rule_id == "R011":
                    assert v.severity == RuleSeverity.HIGH, (
                        "R011 should have original HIGH severity without override"
                    )

    def test_severity_override_to_high(self):
        """Severity override to HIGH should work."""
        config = Config(severity_overrides={"R002": "HIGH"})

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text("x = {1: 2, 3: 4, 5: 6}")

            linter = DtoStrictLinter(config)
            result = linter.lint_path(bad_file)

            for v in result:
                if v.rule_id == "R002":
                    assert v.severity == RuleSeverity.HIGH, (
                        "Override not applied: R002 should have HIGH severity"
                    )

    def test_severity_override_to_medium(self):
        """Severity override to MEDIUM should work."""
        config = Config(
            severity_overrides={"R001": "MEDIUM"}, service_paths=["**/*.py"]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text(
                "from typing import Any\n"
                "class UserService:\n"
                "    def process_user(self, config: dict[str, Any]) -> None:\n"
                "        pass"
            )

            linter = DtoStrictLinter(config)
            result = linter.lint_path(bad_file)

            for v in result:
                if v.rule_id == "R001":
                    assert v.severity == RuleSeverity.MEDIUM, (
                        "Override not applied: R001 should have MEDIUM severity"
                    )


class TestInfoSeverityLevel:
    """Test Fix B: INFO severity level for non-blocking violations."""

    def test_info_severity_exit_code_zero(self):
        """Violations with only INFO severity should exit 0."""
        info_violation = Violation(
            rule_id="R011",
            severity=RuleSeverity.INFO,
            file="test.py",
            line=1,
            col=0,
            message="Test info violation",
        )

        config = Config()
        linter = DtoStrictLinter(config)
        exit_code = linter.get_exit_code([info_violation])

        assert exit_code == 0, "INFO severity should result in exit code 0"

    def test_info_severity_override_r011(self):
        """Override R011 to INFO should exit 0 even when violations present."""
        config = Config(severity_overrides={"R011": "INFO"})

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text('raise ValueError("error message")')

            linter = DtoStrictLinter(config)
            result = linter.lint_path(bad_file)

            exit_code = linter.get_exit_code(result)

            for v in result:
                if v.rule_id == "R011":
                    assert v.severity == RuleSeverity.INFO, "R011 should be INFO"

            assert exit_code == 0, "Exit code should be 0 when only INFO violations"

    def test_info_not_blocking_with_other_violations(self):
        """When INFO and LOW are present, should exit 3 (LOW blocking)."""
        violations = [
            Violation(
                rule_id="R011",
                severity=RuleSeverity.INFO,
                file="test.py",
                line=1,
                col=0,
                message="Info",
            ),
            Violation(
                rule_id="R005",
                severity=RuleSeverity.LOW,
                file="test.py",
                line=2,
                col=0,
                message="Low",
            ),
        ]

        config = Config()
        linter = DtoStrictLinter(config)
        exit_code = linter.get_exit_code(violations)

        assert exit_code == 3, "Exit code should be 3 when LOW violations present"

    def test_high_overrides_info(self):
        """HIGH severity should block even with INFO present."""
        violations = [
            Violation(
                rule_id="R011",
                severity=RuleSeverity.INFO,
                file="test.py",
                line=1,
                col=0,
                message="Info",
            ),
            Violation(
                rule_id="R001",
                severity=RuleSeverity.HIGH,
                file="test.py",
                line=2,
                col=0,
                message="High",
            ),
        ]

        config = Config()
        linter = DtoStrictLinter(config)
        exit_code = linter.get_exit_code(violations)

        assert exit_code == 1, "Exit code should be 1 when HIGH violations present"


class TestNoqaRuleCodeShorthand:
    """Test D3: noqa comments support bare rule codes like # noqa: R006."""

    def test_noqa_bare_rule_code_r006(self):
        """# noqa: R006 should suppress R006."""
        source = "def foo(x: Any): pass  # noqa: R006"
        lines = source.splitlines()
        tree = ast.parse(source)
        func_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(func_node, "R006", lines) is True
        assert AnnotationInspector.has_noqa_comment(func_node, "R001", lines) is False

    def test_noqa_bare_rule_code_r011(self):
        """# noqa: R011 should suppress R011 only."""
        source = "x = 1  # noqa: R011"
        lines = source.splitlines()
        tree = ast.parse(source)
        assign_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(assign_node, "R011", lines) is True
        assert AnnotationInspector.has_noqa_comment(assign_node, "R001", lines) is False

    def test_noqa_comma_separated_bare_codes(self):
        """# noqa: R006, R011 should suppress both R006 and R011."""
        source = "def foo(x: Any): pass  # noqa: R006, R011"
        lines = source.splitlines()
        tree = ast.parse(source)
        func_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(func_node, "R006", lines) is True
        assert AnnotationInspector.has_noqa_comment(func_node, "R011", lines) is True
        assert AnnotationInspector.has_noqa_comment(func_node, "R001", lines) is False

    def test_noqa_bare_code_not_suppressing_other(self):
        """# noqa: R006 should NOT suppress R001."""
        source = "def foo(x: dict[str, Any]): pass  # noqa: R006"
        lines = source.splitlines()
        tree = ast.parse(source)
        func_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(func_node, "R006", lines) is True
        assert AnnotationInspector.has_noqa_comment(func_node, "R001", lines) is False

    def test_noqa_namespaced_still_works(self):
        """Existing # noqa: strict-module-R006 should still work."""
        source = "def foo(x: Any): pass  # noqa: strict-module-R006"
        lines = source.splitlines()
        tree = ast.parse(source)
        func_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(func_node, "R006", lines) is True

    def test_noqa_dto_strict_compat_still_works(self):
        """Existing # noqa: dto-strict-R006 backward-compat should still work."""
        source = "def foo(x: Any): pass  # noqa: dto-strict-R006"
        lines = source.splitlines()
        tree = ast.parse(source)
        func_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(func_node, "R006", lines) is True

    def test_noqa_bare_code_with_explanation(self):
        """# noqa: R006 - explanation should work."""
        source = "def foo(x: Any): pass  # noqa: R006 - legacy payload"
        lines = source.splitlines()
        tree = ast.parse(source)
        func_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(func_node, "R006", lines) is True

    def test_noqa_negative_control_without_comment(self):
        """RED control: Without noqa comment, should return False."""
        source = "def foo(x: Any): pass"
        lines = source.splitlines()
        tree = ast.parse(source)
        func_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(func_node, "R006", lines) is False

    def test_noqa_negative_control_wrong_rule(self):
        """RED control: # noqa: R001 should not suppress R006."""
        source = "def foo(x: Any): pass  # noqa: R001"
        lines = source.splitlines()
        tree = ast.parse(source)
        func_node = tree.body[0]

        assert AnnotationInspector.has_noqa_comment(func_node, "R006", lines) is False


class TestInfoSeverityFormatting:
    """Test that INFO severity is rendered correctly in all formats."""

    def test_format_text_info(self):
        """INFO violations should format correctly as text."""
        violation = Violation(
            rule_id="R011",
            severity=RuleSeverity.INFO,
            file="test.py",
            line=1,
            col=0,
            message="String literal at raise site",
        )

        output = violation.format_text()
        assert "R011" in output
        assert "test.py:1:" in output

    def test_format_github_info(self):
        """INFO violations should use 'notice' level in GitHub format."""
        violation = Violation(
            rule_id="R011",
            severity=RuleSeverity.INFO,
            file="test.py",
            line=1,
            col=0,
            message="String literal at raise site",
        )

        output = violation.format_github()
        assert "::notice" in output
        assert "R011" in output or "String literal" in output

    def test_format_github_high_is_error(self):
        """HIGH violations should use 'error' level in GitHub format."""
        violation = Violation(
            rule_id="R001",
            severity=RuleSeverity.HIGH,
            file="test.py",
            line=1,
            col=0,
            message="Dict[str, Any]",
        )

        output = violation.format_github()
        assert "::error" in output

    def test_format_github_medium_is_warning(self):
        """MEDIUM violations should use 'warning' level in GitHub format."""
        violation = Violation(
            rule_id="R002",
            severity=RuleSeverity.MEDIUM,
            file="test.py",
            line=1,
            col=0,
            message="Inline dict",
        )

        output = violation.format_github()
        assert "::warning" in output
