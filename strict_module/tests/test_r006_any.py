"""Tests for R006: typing.Any in signatures."""

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


def test_r006_any_in_parameter(tmp_path):
    """typing.Any in parameter flagged."""
    bad_file = tmp_path / "services.py"
    bad_file.write_text(
        """
from typing import Any

def process(data: Any) -> None:  # bad: Any in parameter
    pass
"""
    )
    config = Config(
        r006_paths=["**/*.py"],
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(bad_file)
    r006_violations = [v for v in violations if v.rule_id == "R006"]
    assert len(r006_violations) >= 1
    assert any("parameter" in v.message for v in r006_violations)


def test_r006_any_in_return(tmp_path):
    """typing.Any in return type flagged."""
    bad_file = tmp_path / "services.py"
    bad_file.write_text(
        """
from typing import Any

def get_config() -> Any:  # bad: Any in return
    return {}
"""
    )
    config = Config(
        r006_paths=["**/*.py"],
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(bad_file)
    r006_violations = [v for v in violations if v.rule_id == "R006"]
    assert len(r006_violations) >= 1
    assert any("return" in v.message for v in r006_violations)


def test_r006_optional_any(tmp_path):
    """typing.Optional[Any] flagged."""
    bad_file = tmp_path / "services.py"
    bad_file.write_text(
        """
from typing import Optional, Any

def fetch(id: int) -> Optional[Any]:  # bad: Any in Optional
    return None
"""
    )
    config = Config(
        r006_paths=["**/*.py"],
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(bad_file)
    r006_violations = [v for v in violations if v.rule_id == "R006"]
    assert len(r006_violations) >= 1


def test_r006_no_any(tmp_path):
    """Proper types allowed."""
    good_file = tmp_path / "services.py"
    good_file.write_text(
        """
from typing import Dict

def process(data: Dict[str, str]) -> None:
    pass
"""
    )
    config = Config(
        r006_paths=["**/*.py"],
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(good_file)
    r006_violations = [v for v in violations if v.rule_id == "R006"]
    assert len(r006_violations) == 0


def test_r006_scoped_to_r006_paths(tmp_path):
    """R006 respects r006_paths config."""
    # File NOT in r006_paths should not be checked
    other_file = tmp_path / "utils.py"
    other_file.write_text(
        """
from typing import Any

def helper(x: Any) -> Any:  # allowed: not in r006_paths
    return x
"""
    )
    config = Config(
        r006_paths=["**/services/*.py"],  # only services
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(other_file)
    r006_violations = [v for v in violations if v.rule_id == "R006"]
    assert len(r006_violations) == 0
