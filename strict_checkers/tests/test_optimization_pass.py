"""Tests for behaviour fixed during the checker optimization pass."""

import ast
import re
from pathlib import Path

import pytest

from strict_config._config import Config, ConfigLoadError
from strict_inspection import AnnotationInspector
from strict_linter import DtoStrictLinter


def _lint(path: Path, config: Config) -> list:
    """Lint one file with the given config and return all violations."""
    return DtoStrictLinter(config).lint_file(path)


class TestR002FunctionContext:
    """Test suite for R002 function context after a function ends."""

    def test_module_dict_after_tagged_function_is_not_excused(self, tmp_path):
        """A tag on an earlier function does not excuse a module-level dict literal."""
        source = (
            "def tagged():  # FRAMEWORK\n"
            "    return 1\n"
            "\n"
            'DATA = {"a": 1, "b": 2, "c": 3}\n'
        )
        path = tmp_path / "module.py"
        path.write_text(source)

        violations = _lint(path, Config(service_paths=["**/*.py"]))
        r002 = [v for v in violations if v.rule_id == "R002"]

        assert len(r002) == 1
        assert r002[0].line == 4


class TestR003DecoratorKeywordValues:
    """Test suite for R003 decorator keyword values that are bare names."""

    def test_bare_name_keyword_value_is_read_without_error(self, tmp_path):
        """A dataclass keyword set to a bare name is read as text, not crashed on."""
        source = (
            "from dataclasses import dataclass\n"
            "\n"
            "FROZEN = True\n"
            "\n"
            "@dataclass(frozen=FROZEN, slots=True)\n"
            "class Record:\n"
            "    value: int\n"
        )
        path = tmp_path / "dtos.py"
        path.write_text(source)

        violations = _lint(path, Config(r003_mode="strict"))
        r003 = [v for v in violations if v.rule_id == "R003"]

        assert len(r003) == 1
        assert "frozen=True" in r003[0].message


class TestR006AnyMatching:
    """Test suite for R006 matching the typing.Any name, not any identifier containing its letters."""

    def test_identifier_containing_any_letters_is_not_flagged(self, tmp_path):
        """A class named Company is not typing.Any."""
        services = tmp_path / "services"
        services.mkdir()
        path = services / "orders.py"
        path.write_text(
            "class Company:\n"
            "    pass\n"
            "\n"
            "def load_company(company: Company) -> Company:\n"
            "    return company\n"
        )

        violations = _lint(path, Config(r006_paths=["**/services/*.py"]))

        assert [v for v in violations if v.rule_id == "R006"] == []

    def test_qualified_typing_any_is_flagged(self, tmp_path):
        """A parameter annotated typing.Any is still flagged."""
        services = tmp_path / "services"
        services.mkdir()
        path = services / "orders.py"
        path.write_text(
            "import typing\n"
            "\n"
            "def load_order(payload: typing.Any) -> None:\n"
            "    return None\n"
        )

        violations = _lint(path, Config(r006_paths=["**/services/*.py"]))
        r006 = [v for v in violations if v.rule_id == "R006"]

        assert len(r006) == 1
        assert "typing.Any in parameter: load_order" in r006[0].message


class TestR011ConstantsModule:
    """Test suite for R011 exemption of constants modules."""

    def test_file_under_constants_directory_is_exempt(self, tmp_path):
        """A raise with a literal inside a constants directory is not reported."""
        package = tmp_path / "constants"
        package.mkdir()
        path = package / "orders.py"
        path.write_text('raise ValueError("boom")\n')

        violations = _lint(path, Config())

        assert [v for v in violations if v.rule_id == "R011"] == []

    def test_directory_whose_name_only_contains_constants_is_not_exempt(self, tmp_path):
        """A directory such as constantsfoo does not exempt its files."""
        package = tmp_path / "constantsfoo"
        package.mkdir()
        path = package / "orders.py"
        path.write_text('raise ValueError("boom")\n')

        violations = _lint(path, Config())
        r011 = [v for v in violations if v.rule_id == "R011"]

        assert len(r011) == 1


class TestR015TimingRound:
    """Test suite for R015 timing-capture recognition."""

    def test_method_named_round_is_not_a_latency_calculation(self, tmp_path):
        """Only the bare round builtin completes a timing-capture pair."""
        source = (
            "import time\n"
            "\n"
            "def wrapped(value):\n"
            "    try:\n"
            "        start = time.perf_counter()\n"
            "        latency_ms = value.round()\n"
            "        return latency_ms\n"
            "    except ValueError:\n"
            "        raise\n"
        )
        path = tmp_path / "wrap.py"
        path.write_text(source)

        violations = _lint(path, Config())
        r015 = [v for v in violations if v.rule_id == "R015"]

        assert r015 == []


class TestConfigLoadErrors:
    """Test suite for configuration loading errors and defaults."""

    def test_malformed_toml_raises_with_path(self, tmp_path):
        """Invalid TOML raises ConfigLoadError naming the file instead of returning defaults."""
        path = tmp_path / "pyproject.toml"
        path.write_text("[tool.strict-module\nservice_paths = ")

        with pytest.raises(ConfigLoadError, match=re.escape(str(path))):
            Config.from_pyproject(path)

    def test_non_table_section_raises(self, tmp_path):
        """A [tool.strict-module] section that is not a table raises ConfigLoadError."""
        path = tmp_path / "pyproject.toml"
        path.write_text('[tool]\nstrict-module = "oops"\n')

        with pytest.raises(ConfigLoadError, match=re.escape(str(path))):
            Config.from_pyproject(path)

    def test_missing_file_yields_defaults_as_copies(self, tmp_path):
        """A missing file returns defaults; mutating them does not change the shared constants."""
        config = Config.from_pyproject(tmp_path / "absent.toml")
        config.service_paths.append("extra/*.py")

        assert "extra/*.py" not in Config().service_paths

    def test_valid_file_without_section_copies_default_lists(self, tmp_path):
        """A file with no strict-module section copies default lists, not the constants."""
        path = tmp_path / "pyproject.toml"
        path.write_text("[project]\nname = 'x'\n")

        config = Config.from_pyproject(path)
        config.exception_tags.append("local")

        assert "local" not in Config().exception_tags


class TestAnnotationInspectorMatching:
    """Test suite for annotation matching by name rather than by substring."""

    def test_qualified_dict_str_any_is_detected(self):
        """Dict[str, typing.Any] is detected the same as Dict[str, Any]."""
        annotation = ast.parse("Dict[str, typing.Any]", mode="eval").body

        assert AnnotationInspector.is_dict_str_any(annotation) is True

    def test_dict_str_anystr_is_not_dict_str_any(self):
        """Dict[str, AnyStr] names a different type and is not flagged."""
        annotation = ast.parse("Dict[str, AnyStr]", mode="eval").body

        assert AnnotationInspector.is_dict_str_any(annotation) is False

    def test_contains_any_ignores_identifiers_with_those_letters(self):
        """Company and Anything do not contain typing.Any."""
        annotation = ast.parse("Optional[Company]", mode="eval").body

        assert AnnotationInspector.contains_any(annotation) is False

    def test_contains_any_finds_bare_any_inside_optional(self):
        """Optional[Any] still contains typing.Any."""
        annotation = ast.parse("Optional[Any]", mode="eval").body

        assert AnnotationInspector.contains_any(annotation) is True
