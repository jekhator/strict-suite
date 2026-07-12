"""Tests for R001: Bare dict/list/tuple detection with strict_collections mode."""

from pathlib import Path

import pytest

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


@pytest.fixture
def fixture_dir():
    """Get fixtures directory."""
    return Path(__file__).parent / "fixtures"


def test_r001_strict_collections_bare_dict(fixture_dir, tmp_path):
    """Bare dict flagged with strict_collections=True."""
    bad_file = tmp_path / "bad_bare_dict.py"
    bad_file.write_text(
        """
def process_data(config: dict) -> None:  # bad: bare dict
    pass
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        strict_collections=True,
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(bad_file)
    r001_violations = [v for v in violations if v.rule_id == "R001"]
    assert len(r001_violations) >= 1
    assert any("Bare collection" in v.message for v in r001_violations)


def test_r001_strict_collections_bare_list(fixture_dir, tmp_path):
    """Bare list flagged with strict_collections=True."""
    bad_file = tmp_path / "bad_bare_list.py"
    bad_file.write_text(
        """
def get_items() -> list:  # bad: bare list
    return []
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        strict_collections=True,
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(bad_file)
    r001_violations = [v for v in violations if v.rule_id == "R001"]
    assert len(r001_violations) >= 1


def test_r001_strict_collections_bare_tuple(fixture_dir, tmp_path):
    """Bare tuple flagged with strict_collections=True."""
    bad_file = tmp_path / "bad_bare_tuple.py"
    bad_file.write_text(
        """
def unpack_data() -> tuple:  # bad: bare tuple
    return ()
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        strict_collections=True,
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(bad_file)
    r001_violations = [v for v in violations if v.rule_id == "R001"]
    assert len(r001_violations) >= 1


def test_r001_strict_collections_disabled(fixture_dir, tmp_path):
    """Bare dict allowed with strict_collections=False."""
    good_file = tmp_path / "good_bare_dict.py"
    good_file.write_text(
        """
def process_data(config: dict) -> None:  # allowed when strict_collections=False
    pass
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        strict_collections=False,
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(good_file)
    r001_violations = [v for v in violations if v.rule_id == "R001"]
    assert len(r001_violations) == 0


def test_r001_typed_collections_allowed(fixture_dir, tmp_path):
    """Typed dict/list/tuple always allowed."""
    good_file = tmp_path / "good_typed.py"
    good_file.write_text(
        """
def process_data(config: dict[str, str]) -> list[int] -> None:
    pass
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        strict_collections=True,
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(good_file)
    r001_violations = [v for v in violations if v.rule_id == "R001"]
    assert len(r001_violations) == 0
