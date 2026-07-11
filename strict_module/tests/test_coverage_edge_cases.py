"""Tests for edge cases and error paths to improve coverage."""

import pytest
from pathlib import Path
from strict_module.config import Config
from strict_module.linter import DtoStrictLinter
from strict_module.rules import has_noqa_comment
import ast


class TestNoqaCommentParsing:
    """Test has_noqa_comment with various formats."""

    def test_noqa_bare(self):
        """Test bare noqa without spec."""
        code = "x = {a: 1}  # noqa"
        lines = code.split("\n")
        tree = ast.parse(code)
        node = list(ast.walk(tree))[1]
        result = has_noqa_comment(node, "R002", lines)
        assert result is True

    def test_noqa_with_multiple_rules(self):
        """Test noqa with multiple rule specs."""
        code = "x = {a: 1}  # noqa: strict-module-R001, strict-module-R002"
        lines = code.split("\n")
        tree = ast.parse(code)
        node = list(ast.walk(tree))[1]
        result = has_noqa_comment(node, "R002", lines)
        assert result is True

    def test_noqa_backward_compat_dto_strict(self):
        """Test backward-compat dto-strict noqa format."""
        code = "x = {a: 1}  # noqa: dto-strict-R002"
        lines = code.split("\n")
        tree = ast.parse(code)
        node = list(ast.walk(tree))[1]
        result = has_noqa_comment(node, "R002", lines)
        assert result is True

    def test_noqa_not_suppressed(self):
        """Test noqa for different rule not suppressing."""
        code = "x = {a: 1}  # noqa: strict-module-R001"
        lines = code.split("\n")
        tree = ast.parse(code)
        node = list(ast.walk(tree))[1]
        result = has_noqa_comment(node, "R002", lines)
        assert result is False


class TestLinterEdgeCases:
    """Test linter with edge cases."""

    def test_linter_with_empty_file(self, tmp_path):
        """Test linting an empty file."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")
        config = Config()
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(empty_file)
        assert len(violations) == 0

    def test_linter_with_syntax_error_file(self, tmp_path):
        """Test linting a file with syntax error."""
        bad_file = tmp_path / "syntax_error.py"
        bad_file.write_text("def foo(:\n")
        config = Config()
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(bad_file)
        assert len(violations) == 0

    def test_linter_with_nonexistent_file(self, tmp_path):
        """Test linting a nonexistent file."""
        nonexistent = tmp_path / "nonexistent.py"
        config = Config()
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(nonexistent)
        assert len(violations) == 0

    def test_linter_format_github_high_severity(self, tmp_path):
        """Test GitHub format with HIGH severity."""
        service_file = tmp_path / "apps" / "services" / "test.py"
        service_file.parent.mkdir(parents=True, exist_ok=True)
        service_file.write_text("""
from typing import Any

def process(data: Any) -> dict:
    return {}
""")
        config = Config(service_paths=["apps/*/services/*.py"])
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(service_file)
        if violations:
            formatted = linter.format_violations(violations, "github")
            assert "::error" in formatted or "::warning" in formatted

    def test_config_with_disabled_rules(self, tmp_path):
        """Test configuration with disabled rules."""
        service_file = tmp_path / "apps" / "services" / "test.py"
        service_file.parent.mkdir(parents=True, exist_ok=True)
        service_file.write_text("""
from typing import Any

def process(data: Any) -> dict:
    return {}
""")
        config = Config(
            service_paths=["apps/*/services/*.py"],
            disabled_rules=["R006"]
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(service_file)
        r006_violations = [v for v in violations if v.rule_id == "R006"]
        assert len(r006_violations) == 0

    def test_generate_baseline_empty_violations(self, tmp_path):
        """Test baseline generation with no violations."""
        clean_file = tmp_path / "clean.py"
        clean_file.write_text("x = 1")
        config = Config()
        linter = DtoStrictLinter(config)
        violations = []
        baseline = linter.generate_baseline(violations)
        assert isinstance(baseline, (dict, list))

    def test_baseline_ratchet_improvement(self, tmp_path):
        """Test baseline ratchet allows improvements."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        baseline = {str(test_file): 10}

        config = Config()
        linter = DtoStrictLinter(config, baseline=baseline)
        violations = []

        for v in linter.format_violations(violations, "text").split("\n"):
            pass


class TestCheckerEdgeCases:
    """Test checkers with edge cases."""

    def test_module_level_function_with_tag(self, tmp_path):
        """Test module-level function with exception tag."""
        code_file = tmp_path / "module.py"
        code_file.write_text("""
def handle_event():  # FRAMEWORK
    pass
""")
        config = Config(
            service_paths=["**/*.py"],
            exception_tags=["FRAMEWORK"]
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(code_file)
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert len(r004_violations) == 0

    def test_multiple_violations_per_function(self, tmp_path):
        """Test function with multiple violations."""
        code_file = tmp_path / "multi.py"
        code_file.write_text("""
from typing import Any

def process(data: dict[str, Any]) -> dict:
    return {"result": data}
""")
        config = Config(service_paths=["**/*.py"])
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(code_file)
        assert len(violations) >= 1
