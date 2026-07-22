"""Tests for R-baseline ratchet-from-baseline mode (Issue #4)."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from strict_config._config import Config
from strict_linter import DtoStrictLinter


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

    def test_baseline_empty_when_file_missing(self):
        """Baseline: Load returns empty dict if file missing."""
        baseline = DtoStrictLinter.load_baseline(Path("/nonexistent/baseline.json"))
        assert baseline == {}

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
