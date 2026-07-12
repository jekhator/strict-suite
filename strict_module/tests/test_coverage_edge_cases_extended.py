"""Extended coverage tests for checkers, rules, and linter edge cases."""

import ast
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

from strict_module.config import Config
from strict_module.inspection import AnnotationInspector
from strict_module.linter import DtoStrictLinter
from strict_module.rules.rules_client import RuleRegistry


class TestRuleRegistryEdgeCases:
    """Test edge cases in rule registry and rule lookups."""

    def test_get_rule_invalid_id(self):
        """Test getting a rule with invalid ID returns None."""
        rule = RuleRegistry.get_rule("INVALID_RULE")
        assert rule is None

    def test_get_rule_valid_id(self):
        """Test getting a rule with valid ID returns rule."""
        rule = RuleRegistry.get_rule("R001")
        assert rule is not None
        assert rule.id == "R001"

    def test_all_rules_registered(self):
        """Test all expected rule IDs are registered."""
        expected_ids = ["R001", "R002", "R003", "R004", "R005", "R006", "R007", "R008"]
        for rule_id in expected_ids:
            rule = RuleRegistry.get_rule(rule_id)
            assert rule is not None, f"Rule {rule_id} not found"


class TestNoqaCommentEdgeCases:
    """Test edge cases in noqa comment parsing."""

    def test_noqa_malformed_with_em_dash_explanation(self):
        """Test noqa comment with em-dash explanation."""
        source = [
            "x = 1  # noqa: strict-module-R001 — explanation here",
        ]
        node = Mock()
        node.lineno = 1

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is True

    def test_noqa_malformed_with_en_dash_explanation(self):
        """Test noqa comment with en-dash explanation."""
        source = [
            "x = 1  # noqa: strict-module-R001 – explanation",
        ]
        node = Mock()
        node.lineno = 1

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is True

    def test_noqa_malformed_with_regular_dash_explanation(self):
        """Test noqa comment with regular dash explanation."""
        source = [
            "x = 1  # noqa: strict-module-R001 - explanation",
        ]
        node = Mock()
        node.lineno = 1

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is True

    def test_noqa_with_multiple_spaces(self):
        """Test noqa comment with multiple spaces."""
        source = [
            "x = 1  #    noqa:    strict-module-R001",
        ]
        node = Mock()
        node.lineno = 1

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is True

    def test_noqa_bare_noqa_suppresses_all(self):
        """Test bare noqa suppresses all rules."""
        source = [
            "x = 1  # noqa",
        ]
        node = Mock()
        node.lineno = 1

        assert AnnotationInspector.has_noqa_comment(node, "R001", source) is True
        assert AnnotationInspector.has_noqa_comment(node, "R002", source) is True

    def test_noqa_node_without_lineno(self):
        """Test node without lineno attribute."""
        source = ["x = 1"]
        node = Mock(spec=[])

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is False

    def test_noqa_lineno_beyond_source(self):
        """Test lineno beyond source lines."""
        source = ["x = 1"]
        node = Mock()
        node.lineno = 999

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is False

    def test_noqa_lineno_zero(self):
        """Test lineno of 0."""
        source = ["x = 1"]
        node = Mock()
        node.lineno = 0

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is False

    def test_noqa_dto_strict_backward_compat(self):
        """Test backward-compat dto-strict tag."""
        source = [
            "x = 1  # noqa: dto-strict",
        ]
        node = Mock()
        node.lineno = 1

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is True

    def test_noqa_dto_strict_specific_backward_compat(self):
        """Test backward-compat dto-strict-R001 tag."""
        source = [
            "x = 1  # noqa: dto-strict-R001",
        ]
        node = Mock()
        node.lineno = 1

        assert AnnotationInspector.has_noqa_comment(node, "R001", source) is True
        assert AnnotationInspector.has_noqa_comment(node, "R002", source) is False

    def test_noqa_comma_separated_mixed(self):
        """Test comma-separated list with mixed old/new syntax."""
        source = [
            "x = 1  # noqa: dto-strict-R001,strict-module-R002",
        ]
        node = Mock()
        node.lineno = 1

        assert AnnotationInspector.has_noqa_comment(node, "R001", source) is True
        assert AnnotationInspector.has_noqa_comment(node, "R002", source) is True
        assert AnnotationInspector.has_noqa_comment(node, "R003", source) is False

    def test_noqa_no_comment(self):
        """Test line without comment."""
        source = [
            "x = 1",
        ]
        node = Mock()
        node.lineno = 1

        result = AnnotationInspector.has_noqa_comment(node, "R001", source)
        assert result is False


class TestAnnotationParsingEdgeCases:
    """Test edge cases in annotation string parsing."""

    def test_get_annotation_string_name(self):
        """Test annotation string for Name node."""
        source = "def f(x: int): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.get_annotation_string(arg.annotation)
        assert result == "int"

    def test_get_annotation_string_none(self):
        """Test annotation string for None."""
        result = AnnotationInspector.get_annotation_string(None)
        assert result == ""

    def test_get_annotation_string_subscript_simple(self):
        """Test annotation string for simple subscript."""
        source = "def f(x: list[int]): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.get_annotation_string(arg.annotation)
        assert "list" in result.lower()
        assert "int" in result.lower()

    def test_get_annotation_string_tuple(self):
        """Test annotation string for tuple."""
        source = "def f(x: tuple[int, str]): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.get_annotation_string(arg.annotation)
        assert "tuple" in result.lower() or "int" in result.lower()

    def test_get_annotation_string_attribute(self):
        """Test annotation string for attribute."""
        source = "def f(x: typing.Optional[int]): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.get_annotation_string(arg.annotation)
        assert len(result) > 0

    def test_get_annotation_string_constant(self):
        """Test annotation string for constant."""
        source = "x: 'int' = 1"
        tree = ast.parse(source)
        ann_assign = tree.body[0]

        result = AnnotationInspector.get_annotation_string(ann_assign.annotation)
        assert "'int'" in result or "int" in result

    def test_is_dict_str_any_valid(self):
        """Test detection of Dict[str, Any]."""
        source = "from typing import Dict, Any\ndef f(x: Dict[str, Any]): pass"
        tree = ast.parse(source)
        func = tree.body[1]
        arg = func.args.args[0]

        result = AnnotationInspector.is_dict_str_any(arg.annotation)
        assert result is True

    def test_is_dict_str_any_lowercase(self):
        """Test detection of dict[str, any]."""
        source = "def f(x: dict[str, any]): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.is_dict_str_any(arg.annotation)
        assert result is True

    def test_is_dict_str_any_invalid(self):
        """Test detection rejects wrong types."""
        source = "def f(x: dict[str, int]): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.is_dict_str_any(arg.annotation)
        assert result is False

    def test_is_bare_collection_dict(self):
        """Test detection of bare dict."""
        source = "def f(x: dict): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.is_bare_collection(arg.annotation)
        assert result is True

    def test_is_bare_collection_list(self):
        """Test detection of bare list."""
        source = "def f(x: list): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.is_bare_collection(arg.annotation)
        assert result is True

    def test_is_bare_collection_tuple(self):
        """Test detection of bare tuple."""
        source = "def f(x: tuple): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.is_bare_collection(arg.annotation)
        assert result is True

    def test_is_bare_collection_parametrized(self):
        """Test bare collection rejects parametrized."""
        source = "def f(x: list[int]): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.is_bare_collection(arg.annotation)
        assert result is False

    def test_contains_any_present(self):
        """Test detection of Any."""
        source = "from typing import Any\ndef f(x: Any): pass"
        tree = ast.parse(source)
        func = tree.body[1]
        arg = func.args.args[0]

        result = AnnotationInspector.contains_any(arg.annotation)
        assert result is True

    def test_contains_any_in_optional(self):
        """Test detection of Any in Optional."""
        source = "from typing import Optional, Any\ndef f(x: Optional[Any]): pass"
        tree = ast.parse(source)
        func = tree.body[1]
        arg = func.args.args[0]

        result = AnnotationInspector.contains_any(arg.annotation)
        assert result is True

    def test_contains_any_absent(self):
        """Test detection rejects non-Any."""
        source = "def f(x: int): pass"
        tree = ast.parse(source)
        func = tree.body[0]
        arg = func.args.args[0]

        result = AnnotationInspector.contains_any(arg.annotation)
        assert result is False


class TestLinterFileHandling:
    """Test linter file handling and error cases."""

    def test_lint_file_non_python(self):
        """Test linting non-.py file returns empty."""
        config = Config()
        linter = DtoStrictLinter(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            text_file = Path(tmpdir) / "test.txt"
            text_file.write_text("not python")

            result = linter.lint_file(text_file)
            assert result == []

    def test_lint_file_unreadable(self):
        """Test linting unreadable file returns empty."""
        config = Config()
        linter = DtoStrictLinter(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text("x = 1")

            os.chmod(py_file, 0o000)
            try:
                result = linter.lint_file(py_file)
                assert result == []
            finally:
                os.chmod(py_file, 0o644)

    def test_lint_file_invalid_encoding(self):
        """Test linting file with invalid encoding."""
        config = Config()
        linter = DtoStrictLinter(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "test.py"
            py_file.write_bytes(b"\x80\x81\x82\x83")

            result = linter.lint_file(py_file)
            assert result == []

    def test_lint_file_syntax_error(self):
        """Test linting file with syntax error."""
        config = Config()
        linter = DtoStrictLinter(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text("x = (")

            result = linter.lint_file(py_file)
            assert result == []

    def test_lint_path_single_file(self):
        """Test linting single file via lint_path."""
        config = Config()
        linter = DtoStrictLinter(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text("x = 1")

            result = linter.lint_path(py_file)
            assert isinstance(result, list)

    def test_lint_path_directory(self):
        """Test linting directory via lint_path."""
        config = Config()
        linter = DtoStrictLinter(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "test1.py").write_text("x = 1")
            (base / "test2.py").write_text("y = 2")

            result = linter.lint_path(base)
            assert isinstance(result, list)

    def test_lint_path_nonexistent(self):
        """Test linting nonexistent path."""
        config = Config()
        linter = DtoStrictLinter(config)

        result = linter.lint_path(Path("/nonexistent/path"))
        assert result == []

    def test_baseline_filtering_empty_baseline(self):
        """Test baseline filtering with empty baseline."""
        config = Config()
        linter = DtoStrictLinter(config, baseline={})

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text("x = {1: 2, 3: 4, 5: 6}")

            result = linter.lint_file(bad_file)
            assert isinstance(result, list)

    def test_baseline_filtering_with_entries(self):
        """Test baseline filtering with populated baseline."""
        config = Config()

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text("x = {1: 2, 3: 4, 5: 6}")

            baseline = {
                (str(bad_file), 1, "R002"): "abc123",
            }
            linter = DtoStrictLinter(config, baseline=baseline)

            result = linter.lint_file(bad_file)
            filtered = [v for v in result if v.rule_id == "R002" and v.line == 1]
            assert len(filtered) == 0

    def test_load_baseline_valid(self):
        """Test loading valid baseline file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_file = Path(tmpdir) / "baseline.json"
            baseline_file.write_text(
                json.dumps(
                    [
                        {
                            "file": "test.py",
                            "line": 1,
                            "rule_id": "R001",
                            "message_hash": "abc123",
                        }
                    ]
                )
            )

            result = DtoStrictLinter.load_baseline(baseline_file)
            assert ("test.py", 1, "R001") in result

    def test_load_baseline_invalid_json(self):
        """Test loading invalid JSON baseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_file = Path(tmpdir) / "baseline.json"
            baseline_file.write_text("not json")

            result = DtoStrictLinter.load_baseline(baseline_file)
            assert result == {}

    def test_load_baseline_nonexistent(self):
        """Test loading nonexistent baseline file."""
        result = DtoStrictLinter.load_baseline(Path("/nonexistent/baseline.json"))
        assert result == {}

    def test_severity_overrides_high(self):
        """Test severity override to HIGH."""
        config = Config(severity_overrides={"R002": "HIGH"})

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text("x = {1: 2, 3: 4, 5: 6}")

            linter = DtoStrictLinter(config)
            result = linter.lint_path(bad_file)

            for v in result:
                if v.rule_id == "R002":
                    assert v.severity.name == "HIGH"

    def test_get_exit_code_high_severity(self):
        """Test exit code 1 for high severity."""
        from strict_module.rules.rules_objects import RuleSeverity, Violation

        config = Config()
        linter = DtoStrictLinter(config)

        violations = [
            Violation("R001", RuleSeverity.HIGH, "test.py", 1, 0, "Test"),
        ]

        code = linter.get_exit_code(violations)
        assert code == 1

    def test_get_exit_code_medium_severity(self):
        """Test exit code 2 for medium severity."""
        from strict_module.rules.rules_objects import RuleSeverity, Violation

        config = Config()
        linter = DtoStrictLinter(config)

        violations = [
            Violation("R002", RuleSeverity.MEDIUM, "test.py", 1, 0, "Test"),
        ]

        code = linter.get_exit_code(violations)
        assert code == 2

    def test_get_exit_code_low_severity(self):
        """Test exit code 3 for low severity."""
        from strict_module.rules.rules_objects import RuleSeverity, Violation

        config = Config()
        linter = DtoStrictLinter(config)

        violations = [
            Violation("R005", RuleSeverity.LOW, "test.py", 1, 0, "Test"),
        ]

        code = linter.get_exit_code(violations)
        assert code == 3

    def test_get_exit_code_no_violations(self):
        """Test exit code 0 for no violations."""
        config = Config()
        linter = DtoStrictLinter(config)

        code = linter.get_exit_code([])
        assert code == 0

    def test_format_violations_text(self):
        """Test text formatting of violations."""
        from strict_module.rules.rules_objects import RuleSeverity, Violation

        config = Config()
        linter = DtoStrictLinter(config)

        violations = [
            Violation("R001", RuleSeverity.HIGH, "test.py", 1, 0, "Test message"),
        ]

        output = linter.format_violations(violations, "text")
        assert "test.py" in output
        assert "R001" in output
        assert "Test message" in output

    def test_format_violations_json(self):
        """Test JSON formatting of violations."""
        from strict_module.rules.rules_objects import RuleSeverity, Violation

        config = Config()
        linter = DtoStrictLinter(config)

        violations = [
            Violation("R001", RuleSeverity.HIGH, "test.py", 1, 0, "Test message"),
        ]

        output = linter.format_violations(violations, "json")
        data = json.loads(output)

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["rule_id"] == "R001"
        assert data[0]["severity"] == "HIGH"

    def test_format_violations_github(self):
        """Test GitHub formatting of violations."""
        from strict_module.rules.rules_objects import RuleSeverity, Violation

        config = Config()
        linter = DtoStrictLinter(config)

        violations = [
            Violation("R001", RuleSeverity.HIGH, "test.py", 1, 0, "Test message"),
        ]

        output = linter.format_violations(violations, "github")
        assert "::error" in output
        assert "file=test.py" in output
        assert "line=1" in output
