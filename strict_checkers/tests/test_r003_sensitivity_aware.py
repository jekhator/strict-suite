"""Tests for R003 sensitivity-aware repr=False exception."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR003SensitivityAware:
    """Test suite for sensitivity-aware repr=False exception."""

    def test_r003_bare_repr_false_still_flags(self, tmp_path):
        """repr=False without sensitivity still flags (negative control)."""
        bad_file = tmp_path / "dtos.py"
        bad_file.write_text(
            """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, repr=False)
class PlainDTO:
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="canonical",
            r003_strict_repr=True,
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(bad_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) >= 1
        assert any("repr=False" in v.message for v in r003_violations)

    def test_r003_sensitivity_base_allows_repr_false(self, tmp_path):
        """repr=False allowed when class inherits SensitiveRepr base."""
        good_file = tmp_path / "dtos.py"
        good_file.write_text(
            """
from dataclasses import dataclass
from mixin_sensitivity import SensitiveRepr

@dataclass(frozen=True, slots=True, repr=False)
class SensitiveDTO(SensitiveRepr):
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="canonical",
            r003_strict_repr=True,
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(good_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) == 0

    def test_r003_sensitivity_field_metadata_allows_repr_false(self, tmp_path):
        """repr=False allowed when class has sensitivity field metadata."""
        good_file = tmp_path / "dtos.py"
        good_file.write_text(
            """
from dataclasses import dataclass, field
from mixin_sensitivity import Sensitivity

@dataclass(frozen=True, slots=True, repr=False)
class SensitiveDTO:
    name: str
    ssn: str = field(metadata={"sensitivity": Sensitivity.PII})
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="canonical",
            r003_strict_repr=True,
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(good_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) == 0

    def test_r003_allowlist_by_class_name_allows_repr_false(self, tmp_path):
        """repr=False allowed when class is in allowlist by name."""
        good_file = tmp_path / "dtos.py"
        good_file.write_text(
            """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, repr=False)
class AllowlistedDTO:
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="canonical",
            r003_strict_repr=True,
            r003_sensitivity_allowlist=["AllowlistedDTO"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(good_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) == 0

    def test_r003_allowlist_by_full_path_allows_repr_false(self, tmp_path):
        """repr=False allowed when class is in allowlist by full path."""
        good_file = tmp_path / "dtos.py"
        good_file.write_text(
            """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, repr=False)
class FullPathAllowlistedDTO:
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="canonical",
            r003_strict_repr=True,
            r003_sensitivity_allowlist=["dtos.FullPathAllowlistedDTO"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(good_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) == 0

    def test_r003_multiple_sensitivity_bases_allowed(self, tmp_path):
        """repr=False allowed with custom sensitivity bases in config."""
        good_file = tmp_path / "dtos.py"
        good_file.write_text(
            """
from dataclasses import dataclass

class CustomSensitiveBase:
    pass

@dataclass(frozen=True, slots=True, repr=False)
class SensitiveDTO(CustomSensitiveBase):
    name: str
"""
        )
        config = Config(
            dto_paths=["**/*.py"],
            r003_mode="canonical",
            r003_strict_repr=True,
            r003_sensitivity_bases=["SensitiveRepr", "CustomSensitiveBase"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(good_file)
        r003_violations = [v for v in violations if v.rule_id == "R003"]
        assert len(r003_violations) == 0
