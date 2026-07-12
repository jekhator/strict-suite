"""Tests for R002 configurable min_dict_keys threshold (Issue #2)."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestR002ConfigurableThreshold:
    """Test suite for related functionality."""

    def test_r002_threshold_2_keys(self):
        """R002: With min_dict_keys=2, 2+ string keys trigger violation."""
        source = """
def build_response():
    return {
        "key1": "value1",
        "key2": "value2",
    }
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                service_paths=["**/*.py"],
                min_dict_keys=2,  # Lower threshold
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r002_violations = [v for v in violations if v.rule_id == "R002"]
            assert len(r002_violations) >= 1, (
                "2 keys should trigger with min_dict_keys=2"
            )
        finally:
            path.unlink()

    def test_r002_threshold_3_keys_default(self):
        """R002: Default min_dict_keys=3, 2 keys should be OK."""
        source = """
def build_response():
    return {
        "key1": "value1",
        "key2": "value2",
    }
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                service_paths=["**/*.py"],
                min_dict_keys=3,  # Default
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r002_violations = [v for v in violations if v.rule_id == "R002"]
            assert len(r002_violations) == 0, "2 keys should be OK with min_dict_keys=3"
        finally:
            path.unlink()

    def test_r002_threshold_5_keys(self):
        """R002: With min_dict_keys=5, 4 keys should be OK, 5+ should violate."""
        source = """
def build_response():
    return {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
        "key4": "value4",
    }
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                service_paths=["**/*.py"],
                min_dict_keys=5,
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r002_violations = [v for v in violations if v.rule_id == "R002"]
            assert len(r002_violations) == 0, "4 keys should be OK with min_dict_keys=5"
        finally:
            path.unlink()

    def test_r002_threshold_5_keys_trigger(self):
        """R002: With min_dict_keys=5, 5+ keys should trigger."""
        source = """
def build_response():
    return {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
        "key4": "value4",
        "key5": "value5",
    }
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(
                service_paths=["**/*.py"],
                min_dict_keys=5,
            )
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            r002_violations = [v for v in violations if v.rule_id == "R002"]
            assert len(r002_violations) >= 1, (
                "5+ keys should trigger with min_dict_keys=5"
            )
        finally:
            path.unlink()
