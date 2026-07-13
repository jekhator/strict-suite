"""Comprehensive tests for checker edge cases and uncovered paths."""

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestR001VarArgKwarg:
    """Test R001 coverage for vararg and kwarg cases."""

    def test_r001_bad_vararg_dict_str_any(self, fixture_dir):
        """Bad: Dict[str, Any] in *args."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r001_bad_vararg_dict_str_any.py"
        )
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) >= 1
        assert any("Dict[str, Any]" in v.message for v in r001_violations)

    def test_r001_bad_kwarg_dict_str_any(self, fixture_dir):
        """Bad: Dict[str, Any] in **kwargs."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r001_bad_kwarg_dict_str_any.py"
        )
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) >= 1
        assert any("Dict[str, Any]" in v.message for v in r001_violations)

    def test_r001_bad_vararg_bare_collection(self, fixture_dir):
        """Bad: bare dict in *args with strict_collections=True."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            strict_collections=True,
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r001_bad_vararg_bare_collection.py"
        )
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) >= 1
        assert any("Bare collection type" in v.message for v in r001_violations)

    def test_r001_bad_kwarg_bare_collection(self, fixture_dir):
        """Bad: bare list in **kwargs with strict_collections=True."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            strict_collections=True,
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r001_bad_kwarg_bare_collection.py"
        )
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) >= 1
        assert any("Bare collection type" in v.message for v in r001_violations)


class TestR006VarArgKwarg:
    """Test R006 coverage for vararg and kwarg cases."""

    def test_r006_bad_vararg_any(self, fixture_dir):
        """Bad: typing.Any in *args."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            r006_paths=["**/*.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r006_bad_vararg_any.py")
        r006_violations = [v for v in violations if v.rule_id == "R006"]
        assert len(r006_violations) >= 1
        assert any("*args" in v.message for v in r006_violations)

    def test_r006_bad_kwarg_any(self, fixture_dir):
        """Bad: typing.Any in **kwargs."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            r006_paths=["**/*.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r006_bad_kwarg_any.py")
        r006_violations = [v for v in violations if v.rule_id == "R006"]
        assert len(r006_violations) >= 1
        assert any("**kwargs" in v.message for v in r006_violations)


class TestR007FixtureDecorators:
    """Test R007 coverage for different fixture decorator forms."""

    def test_r007_bad_bare_fixture_decorator(self, fixture_dir):
        """Bad: @fixture decorator (bare import from pytest)."""
        config = Config(
            service_paths=["**/services.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "test_r007_bare_fixture_decorator.py"
        )
        r007_violations = [v for v in violations if v.rule_id == "R007"]
        assert len(r007_violations) >= 1
        assert any("conftest.py" in v.message for v in r007_violations)

    def test_r007_bad_fixture_with_call(self, fixture_dir):
        """Bad: @pytest.fixture(scope="function") form."""
        config = Config(
            service_paths=["**/services.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "test_r007_fixture_with_call.py"
        )
        r007_violations = [v for v in violations if v.rule_id == "R007"]
        assert len(r007_violations) >= 1
        assert any("conftest.py" in v.message for v in r007_violations)


class TestR001Suppressed:
    """Test R001 with noqa suppression."""

    def test_r001_suppressed_vararg_dict_str_any(self, tmp_path):
        """Suppressed: Dict[str, Any] in *args with noqa."""
        code = '''"""Service file."""
from typing import Any, Dict

class ServiceClass:
    """Service with suppressed bad vararg."""

    def process(self, *args: Dict[str, Any]) -> None:  # noqa: strict-module-R001
        """Process."""
        pass
'''
        test_file = tmp_path / "service.py"
        test_file.write_text(code)

        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) == 0


class TestR006Suppressed:
    """Test R006 with noqa suppression."""

    def test_r006_suppressed_vararg_any(self, tmp_path):
        """Suppressed: typing.Any in *args with noqa."""
        code = '''"""Service file."""
from typing import Any

class ServiceClass:
    """Service with suppressed bad vararg."""

    def process(self, *args: Any) -> None:  # noqa: strict-module-R006
        """Process."""
        pass
'''
        test_file = tmp_path / "service.py"
        test_file.write_text(code)

        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            r006_paths=["**/*.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r006_violations = [v for v in violations if v.rule_id == "R006"]
        assert len(r006_violations) == 0


class TestR007Suppressed:
    """Test R007 with noqa suppression."""

    def test_r007_suppressed_fixture(self, tmp_path):
        """Suppressed: fixture outside conftest with noqa."""
        code = '''"""Test file."""
import pytest

def test_something():
    """A test function."""
    pass

@pytest.fixture
def my_resource():  # noqa: strict-module-R007
    """A fixture with noqa."""
    return "resource"
'''
        test_file = tmp_path / "test_something.py"
        test_file.write_text(code)

        config = Config(
            service_paths=["**/services.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r007_violations = [v for v in violations if v.rule_id == "R007"]
        assert len(r007_violations) == 0


class TestR002TagJustification:
    """Test R002 exception tag justification."""

    def test_r002_bad_tag_no_justification(self, fixture_dir):
        """Bad: exception tag without justification when required."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            exception_tag_requires_justification=True,
            exception_tags=["facade"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r002_bad_dict_no_justification.py"
        )
        r002_violations = [v for v in violations if v.rule_id == "R002"]
        assert any("justification" in v.message.lower() for v in r002_violations)

    def test_r002_bad_max_tags_exceeded(self, fixture_dir):
        """Bad: exceeding max exception tags per file."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            exception_tag_requires_justification=False,
            exception_tags=["facade"],
            max_exception_tags_per_file=2,
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "r002_bad_dict_max_tags_exceeded.py"
        )
        r002_violations = [v for v in violations if v.rule_id == "R002"]
        assert any("Exceeded max" in v.message for v in r002_violations)
