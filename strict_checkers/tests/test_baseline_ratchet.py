"""Tests for R-baseline ratchet-from-baseline mode (Issue #4)."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from strict_config._config import Config
from strict_config.constants import (
    ERR_BASELINE_ENTRY_NOT_OBJECT,
    ERR_BASELINE_ENTRY_SHAPE,
    ERR_BASELINE_INVALID_JSON,
    ERR_BASELINE_MISSING,
    ERR_BASELINE_NOT_LIST,
)
from strict_linter import BaselineLoadError, DtoStrictLinter


class TestBaselineRatchet:
    """Test suite for related functionality."""

    def test_baseline_generate(self):
        """Baseline: Generate baseline JSON from violations."""
        source = """
def bad_function(x: Dict[str, Any]):
    return {"key": "value"}
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(service_paths=["**/*.py"])
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)
            assert len(violations) > 0, "Should have violations to baseline"

            baseline_data = linter.generate_baseline(violations)
            assert isinstance(baseline_data, list)
            assert len(baseline_data) > 0
            assert "file" in baseline_data[0]
            assert "line" in baseline_data[0]
            assert "rule_id" in baseline_data[0]
            assert "message_hash" in baseline_data[0]
        finally:
            path.unlink()

    def test_baseline_load(self):
        """Baseline: Load baseline JSON file."""
        baseline_json = [
            {
                "file": "test.py",
                "line": 10,
                "rule_id": "R001",
                "message_hash": "abc123",
            },
            {
                "file": "test.py",
                "line": 20,
                "rule_id": "R002",
                "message_hash": "def456",
            },
        ]

        with TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "baseline.json"
            baseline_path.write_text(json.dumps(baseline_json))

            baseline = DtoStrictLinter.load_baseline(baseline_path)
            assert ("test.py", 10, "R001") in baseline
            assert baseline[("test.py", 10, "R001")] == "abc123"
            assert ("test.py", 20, "R002") in baseline
            assert baseline[("test.py", 20, "R002")] == "def456"

    def test_baseline_ratchet_filters_accepted_violations(self):
        """Baseline ratchet: Violations in baseline are filtered (accepted debt)."""
        source = """
def bad_function(x: Dict[str, Any]):
    return {"key": "value", "foo": "bar"}
"""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_file.py"
            path.write_text(source)

            config = Config(service_paths=["**/*.py"])
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(path)

            # First, generate baseline from current violations
            baseline_data = linter.generate_baseline(violations)
            baseline = {}
            for entry in baseline_data:
                key = (entry["file"], entry["line"], entry["rule_id"])
                baseline[key] = entry["message_hash"]

            # Now lint again with baseline loaded
            linter_with_baseline = DtoStrictLinter(config, baseline=baseline)
            violations_filtered = linter_with_baseline.lint_file(path)

            # All violations should be filtered (in baseline)
            assert len(violations_filtered) == 0, (
                f"Baseline violations should be filtered. Got {violations_filtered}"
            )

    def test_baseline_ratchet_new_violations(self):
        """Baseline ratchet: New violations (not in baseline) trigger exit 1."""
        source_original = """
def bad_function_1(x: Dict[str, Any]):
    return {"key": "value"}
"""
        source_new = """
def bad_function_1(x: Dict[str, Any]):
    return {"key": "value"}

def bad_function_2(x: Dict[str, Any]):
    return {"foo": "bar"}
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source_original)
            f.flush()
            path = Path(f.name)

        try:
            config = Config(service_paths=["**/*.py"])

            # Generate baseline from original
            linter = DtoStrictLinter(config)
            violations_original = linter.lint_file(path)
            baseline_data = linter.generate_baseline(violations_original)
            baseline = {}
            for entry in baseline_data:
                key = (entry["file"], entry["line"], entry["rule_id"])
                baseline[key] = entry["message_hash"]

            # Now update file with new violation
            path.write_text(source_new)

            # Lint with baseline
            linter_with_baseline = DtoStrictLinter(config, baseline=baseline)
            violations_new = linter_with_baseline.lint_file(path)

            # Should detect new violation not in baseline
            assert len(violations_new) > 0, "New violations should not be filtered"
        finally:
            path.unlink()

    def test_baseline_missing_file_raises_error(self):
        """Baseline: Load raises BaselineLoadError if file missing."""
        baseline_path = Path("/nonexistent/baseline.json")
        with pytest.raises(BaselineLoadError) as caught:
            DtoStrictLinter.load_baseline(baseline_path)
        assert str(caught.value) == ERR_BASELINE_MISSING.format(path=baseline_path)

    def test_baseline_entry_hash_consistency(self):
        """Baseline: Message hash is consistent across runs."""
        message = "Test violation message"
        hash1 = DtoStrictLinter._hash_message(message)
        hash2 = DtoStrictLinter._hash_message(message)
        assert hash1 == hash2, "Hash should be deterministic"

        hash_different = DtoStrictLinter._hash_message("Different message")
        assert hash1 != hash_different, (
            "Different messages should have different hashes"
        )

    def test_baseline_invalid_json_raises_error(self):
        """Baseline: Load raises BaselineLoadError on invalid JSON."""
        with TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "baseline.json"
            baseline_path.write_text("{ invalid json }")
            with pytest.raises(BaselineLoadError) as caught:
                DtoStrictLinter.load_baseline(baseline_path)
            assert str(caught.value) == ERR_BASELINE_INVALID_JSON.format(
                path=baseline_path
            )

    def test_baseline_not_list_raises_error(self):
        """Baseline: Load raises BaselineLoadError if top level not a list."""
        with TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "baseline.json"
            baseline_path.write_text('{"violations": []}')
            with pytest.raises(BaselineLoadError) as caught:
                DtoStrictLinter.load_baseline(baseline_path)
            assert str(caught.value) == ERR_BASELINE_NOT_LIST.format(path=baseline_path)

    @pytest.mark.parametrize("missing_key", ["file", "line", "rule_id", "message_hash"])
    def test_baseline_entry_missing_key_raises_error(self, missing_key):
        """Baseline: Load raises BaselineLoadError if entry missing required key."""
        with TemporaryDirectory() as tmpdir:
            baseline_json = [
                {
                    "file": "test.py",
                    "line": 10,
                    "rule_id": "R001",
                    "message_hash": "abc123",
                }
            ]
            del baseline_json[0][missing_key]

            baseline_path = Path(tmpdir) / "baseline.json"
            baseline_path.write_text(json.dumps(baseline_json))

            with pytest.raises(BaselineLoadError) as caught:
                DtoStrictLinter.load_baseline(baseline_path)
            assert str(caught.value) == ERR_BASELINE_ENTRY_SHAPE.format(
                index=0, key=missing_key, path=baseline_path
            )

    def test_baseline_entry_not_dict_raises_error(self):
        """Baseline: Load raises BaselineLoadError if entry is not a dict."""
        with TemporaryDirectory() as tmpdir:
            baseline_json = ["not a dict"]
            baseline_path = Path(tmpdir) / "baseline.json"
            baseline_path.write_text(json.dumps(baseline_json))

            with pytest.raises(BaselineLoadError) as caught:
                DtoStrictLinter.load_baseline(baseline_path)
            assert str(caught.value) == ERR_BASELINE_ENTRY_NOT_OBJECT.format(
                index=0, path=baseline_path
            )

    def test_baseline_undecodable_bytes_raises_error(self):
        """Baseline: Load raises BaselineLoadError on undecodable (non-UTF-8) bytes."""
        with TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "baseline.json"
            baseline_path.write_bytes(b"\xff\xfe\x00\x01")

            with pytest.raises(BaselineLoadError) as caught:
                DtoStrictLinter.load_baseline(baseline_path)
            assert str(caught.value) == ERR_BASELINE_INVALID_JSON.format(
                path=baseline_path
            )

    def test_baseline_generate_then_load_round_trip(self):
        """Baseline: Generate-then-load round-trip preserves violations."""
        source = """
def bad_function(x: Dict[str, Any]):
    return {"key": "value"}
"""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(source)

            config = Config(service_paths=["**/*.py"])
            linter = DtoStrictLinter(config)
            violations = linter.lint_file(test_file)
            assert len(violations) > 0, "Should have violations to baseline"

            baseline_data = linter.generate_baseline(violations)
            baseline_path = Path(tmpdir) / "baseline.json"
            baseline_path.write_text(json.dumps(baseline_data))

            loaded_baseline = DtoStrictLinter.load_baseline(baseline_path)
            assert len(loaded_baseline) == len(violations)
            for v in violations:
                key = (v.file, v.line, v.rule_id)
                assert key in loaded_baseline
                assert loaded_baseline[key] == linter._hash_message(v.message)
