"""Tests for R003 strict/relaxed modes (Issue #3)."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestR003StrictRelaxed:
    """Test suite for related functionality."""

    def test_r003_strict_mode_flags_repr_false(self):
        """R003 strict mode (default): repr=False is anti-canonical and flagged."""
        source = """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, repr=False)
class UserDTO:
    user_id: int
    name: str
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                dto_paths=["**/*.py"],
                r003_mode="canonical",
                r003_strict_repr=True,  # Strict mode (default)
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r003_violations = [v for v in violations if v.rule_id == "R003"]
            assert len(r003_violations) >= 1, "repr=False should be flagged in strict mode"
        finally:
            path.unlink()

    def test_r003_strict_mode_accepts_no_repr(self):
        """R003 strict mode: repr=False absent is OK."""
        source = """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class UserDTO:
    user_id: int
    name: str
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                dto_paths=["**/*.py"],
                r003_mode="canonical",
                r003_strict_repr=True,  # Strict mode
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r003_violations = [v for v in violations if v.rule_id == "R003"]
            assert len(r003_violations) == 0, (
                "repr=False absent should be OK in strict mode"
            )
        finally:
            path.unlink()

    def test_r003_relaxed_mode_ignores_repr_false(self):
        """R003 relaxed mode: repr=False is ignored, only checks frozen+slots."""
        source = """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, repr=False)
class UserDTO:
    user_id: int
    name: str
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                dto_paths=["**/*.py"],
                r003_mode="canonical",
                r003_strict_repr=False,  # Relaxed mode
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r003_violations = [v for v in violations if v.rule_id == "R003"]
            assert len(r003_violations) == 0, "repr=False should be ignored in relaxed mode"
        finally:
            path.unlink()

    def test_r003_relaxed_mode_checks_frozen_slots(self):
        """R003 relaxed mode: still checks frozen+slots even if repr=False ignored."""
        source = """
from dataclasses import dataclass

@dataclass(repr=False)
class UserDTO:
    user_id: int
    name: str
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                dto_paths=["**/*.py"],
                r003_mode="canonical",
                r003_strict_repr=False,  # Relaxed mode
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r003_violations = [v for v in violations if v.rule_id == "R003"]
            assert len(r003_violations) >= 1, (
                "Missing frozen+slots should still be flagged in relaxed mode"
            )
        finally:
            path.unlink()

    def test_r003_relaxed_mode_accepts_frozen_slots_only(self):
        """R003 relaxed mode: frozen+slots is sufficient."""
        source = """
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class UserDTO:
    user_id: int
    name: str
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                dto_paths=["**/*.py"],
                r003_mode="canonical",
                r003_strict_repr=False,  # Relaxed mode
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r003_violations = [v for v in violations if v.rule_id == "R003"]
            assert len(r003_violations) == 0, (
                "frozen+slots should be sufficient in relaxed mode"
            )
        finally:
            path.unlink()
