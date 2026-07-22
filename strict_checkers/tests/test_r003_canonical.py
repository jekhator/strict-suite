"""Tests for R003: Canonical mode (repr=False as anti-canonical)."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR003Canonical:
    """Test suite for related functionality."""

    def test_r003_canonical_mode_flags_repr_false(self, tmp_path):
        """repr=False flagged as anti-canonical in canonical mode."""
        bad_file = tmp_path / "dtos.py"
        bad_file.write_text(
            """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, repr=False)
class MyDTO:
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="canonical",
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(bad_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) >= 1
        assert any("repr=False" in v.message for v in r003_violations)

    def test_r003_canonical_mode_allows_no_repr(self, tmp_path):
        """Missing repr=False allowed (canonical) in canonical mode."""
        good_file = tmp_path / "dtos.py"
        good_file.write_text(
            """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class MyDTO:
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="canonical",
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(good_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) == 0

    def test_r003_legacy_mode_requires_repr_false(self, tmp_path):
        """Missing repr=False flagged in legacy mode (v0.1 behavior)."""
        bad_file = tmp_path / "dtos.py"
        bad_file.write_text(
            """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class MyDTO:
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="legacy",
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(bad_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) >= 1
        assert any("repr=False" in v.message for v in r003_violations)

    def test_r003_legacy_mode_allows_repr_false(self, tmp_path):
        """repr=False allowed in legacy mode."""
        good_file = tmp_path / "dtos.py"
        good_file.write_text(
            """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, repr=False)
class MyDTO:
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="legacy",
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(good_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) == 0
