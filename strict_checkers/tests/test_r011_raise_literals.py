"""Tests for R011: String literal at raise site."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR011RaiseLiterals:
    """Test suite for R011 string literal in raise detection."""

    def test_r011_detects_literal_messages(self, fixture_dir):
        """R011 should flag string literals in raise statements."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r011_raise_literal_message.py"
        )
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 4, (
            f"Expected 4 R011 violations (plain literal, f-string, keyword arg literal, "
            f"f-string), got {len(r011_violations)}"
        )

    def test_r011_allows_const_references(self, fixture_dir):
        """R011 should allow const.ERR_* references."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "good" / "r011_const_reference_raise.py"
        )
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, (
            f"Expected 0 R011 violations (all use const references), "
            f"got {len(r011_violations)}: {r011_violations}"
        )

    def test_r011_exempts_test_files(self, fixture_dir):
        """R011 should not flag violations in test files."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "good" / "test_r008_good_test_class.py"
        )
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, (
            "R011 should not flag violations in test files"
        )

    def test_r011_message_suggests_fix(self, fixture_dir):
        """R011 violation message should suggest const extraction."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r011_raise_literal_message.py"
        )
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) > 0
        message = r011_violations[0].message
        assert "constants" in message.lower(), (
            "Message should mention extracting to constants module"
        )
        assert "const" in message.lower(), "Message should mention const reference"

    def test_r011_bare_reraise_allowed(self, tmp_path):
        """R011 should allow bare re-raise without exception."""
        test_file = tmp_path / "test_bare_raise.py"
        test_file.write_text("""
def handle_error():
    try:
        something()
    except Exception:
        raise
""")
        config = Config(
            service_paths=[str(tmp_path / "*.py")],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, "R011 should allow bare re-raise"

    def test_r011_no_args_raise_allowed(self, tmp_path):
        """R011 should allow raise with no arguments."""
        test_file = tmp_path / "test_no_args.py"
        test_file.write_text("""
class Handler:
    def handle_error(self):
        if True:
            raise ValueError()
""")
        config = Config(
            service_paths=[str(tmp_path / "*.py")],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, "R011 should allow raise with no arguments"

    def test_r011_non_call_exception_allowed(self, tmp_path):
        """R011 should allow raise with non-Call exception."""
        test_file = tmp_path / "test_non_call.py"
        test_file.write_text("""
class Handler:
    def handle_error(self, exc):
        raise exc
""")
        config = Config(
            service_paths=[str(tmp_path / "*.py")],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, (
            "R011 should allow non-Call exception (direct re-raise)"
        )

    def test_r011_suppressed_with_noqa(self, tmp_path):
        """R011 violations can be suppressed with noqa in service files."""
        test_file = tmp_path / "handler_noqa.py"
        test_file.write_text("""
class Handler:
    def handle_error(self):
        raise ValueError("error message")  # noqa: dto-strict-R011
""")
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, "R011 should respect noqa comments"

    def test_r011_mixed_arguments(self, tmp_path):
        """R011 should catch literal in any argument position."""
        test_file = tmp_path / "handler.py"
        test_file.write_text("""
import constants as const

class Handler:
    def handle_error(self):
        raise ValueError(const.ERR_X, "extra message")
""")
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 1, (
            f"R011 should catch literal in second argument, got {len(r011_violations)}"
        )

    def test_r011_exempts_constants_module(self, tmp_path):
        """R011 should exempt files in constants modules."""
        test_file = tmp_path / "errors_const.py"
        test_file.write_text("""
def create_error(msg):
    raise ValueError("inline message")

ERR_X = "some error"
""")
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, "R011 should exempt constants modules"

    def test_r011_from_clause_only_checks_exception(self, tmp_path):
        """R011 should check raise from separately, ignoring from clause."""
        test_file = tmp_path / "handler2.py"
        test_file.write_text("""
import constants as const

class Handler:
    def handle_error(self, exc):
        try:
            x = 1 / 0
        except Exception as e:
            raise ValueError(const.ERR_X) from e
""")
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, (
            "R011 should allow raise from with const reference"
        )

    def test_r011_bare_reraise_in_service_path(self, tmp_path):
        """R011 should allow bare re-raise even in service paths."""
        test_file = tmp_path / "service.py"
        test_file.write_text("""
class MyService:
    def process(self):
        try:
            do_work()
        except ValueError:
            raise
""")
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, (
            "R011 should allow bare re-raise in service files"
        )

    def test_r011_non_call_raise_in_service_path(self, tmp_path):
        """R011 should allow raising non-Call exception types."""
        test_file = tmp_path / "service2.py"
        test_file.write_text("""
import sys

class MyService:
    def process(self):
        try:
            do_work()
        except Exception as e:
            exc = ValueError(sys.exc_info()[1])
            raise exc
""")
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 0, (
            "R011 should allow raising variables in service files"
        )

    def test_r011_keyword_argument_literal(self, tmp_path):
        """R011 should flag string literals in keyword arguments."""
        test_file = tmp_path / "bad_kwargs.py"
        test_file.write_text("""
class MyService:
    def process(self):
        raise ValueError(message="inline error string")
""")
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r011_violations = [v for v in violations if v.rule_id == "R011"]

        assert len(r011_violations) == 1, (
            f"R011 should catch keyword argument literals, got {len(r011_violations)}"
        )
