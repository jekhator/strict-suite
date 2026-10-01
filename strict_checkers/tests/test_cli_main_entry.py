"""Tests for CLI main() entry point with direct calls."""

import io
import json
import sys

from strict_config.constants import (
    ERR_BASELINE_INVALID_JSON,
    ERR_BASELINE_MISSING,
    MSG_BASELINE_LOADED,
)
from strict_module.cli import main


class TestCLIMainDirect:
    """Test main() function with direct calls."""

    def test_main_with_loc_cap_flag(self, tmp_path):
        """Test main() dispatches to loc-cap when flag present."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.strict-module]
service_paths = ["**/*.py"]
""")

        original_argv = sys.argv
        try:
            sys.argv = ["strict-module", "loc-cap", str(tmp_path)]
            result = main()
            assert result in [0, 1]
        finally:
            sys.argv = original_argv

    def test_main_no_path_argument(self):
        """Test main() error when no path provided."""
        original_argv = sys.argv
        try:
            sys.argv = ["strict-module"]
            result = main()
            assert result == 1
        finally:
            sys.argv = original_argv

    def test_main_with_multiple_paths(self, tmp_path):
        """Test main() with multiple file paths."""
        file1 = tmp_path / "file1.py"
        file1.write_text("x = 1")
        file2 = tmp_path / "file2.py"
        file2.write_text("y = 2")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.strict-module]
""")

        original_argv = sys.argv
        try:
            sys.argv = ["strict-module", str(file1), str(file2)]
            result = main()
            assert result in [0, 1]
        finally:
            sys.argv = original_argv

    def test_main_with_config_flag(self, tmp_path):
        """Test main() with --config flag."""
        pyproject = tmp_path / "custom.toml"
        pyproject.write_text("""
[tool.strict-module]
""")

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        original_argv = sys.argv
        try:
            sys.argv = ["strict-module", str(test_file), "--config", str(pyproject)]
            result = main()
            assert result == 0
        finally:
            sys.argv = original_argv

    def test_main_baseline_generation_with_path(self, tmp_path):
        """Test main() baseline generation."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.strict-module]
""")

        original_argv = sys.argv
        original_stdout = sys.stdout
        try:
            import io

            sys.stdout = io.StringIO()
            sys.argv = ["strict-module", str(test_file), "--generate-baseline"]
            result = main()
            assert result == 0
        finally:
            sys.argv = original_argv
            sys.stdout = original_stdout

    def test_main_with_baseline_file(self, tmp_path):
        """Test main() with baseline file."""
        baseline_data = [
            {
                "file": "test.py",
                "line": 10,
                "rule_id": "R001",
                "message_hash": "abc123",
            }
        ]
        baseline_file = tmp_path / "baseline.json"
        baseline_file.write_text(json.dumps(baseline_data))

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.strict-module]
""")

        original_argv = sys.argv
        original_stderr = sys.stderr
        try:
            sys.stderr = io.StringIO()
            sys.argv = [
                "strict-module",
                str(test_file),
                "--baseline",
                str(baseline_file),
            ]
            result = main()
            stderr_output = sys.stderr.getvalue()
            assert result == 0
            assert stderr_output.strip() == MSG_BASELINE_LOADED.format(
                count=1, path=baseline_file
            )
        finally:
            sys.argv = original_argv
            sys.stderr = original_stderr

    def test_main_with_missing_baseline_file(self, tmp_path):
        """Test main() with missing baseline file."""
        baseline_file = tmp_path / "nonexistent-baseline.json"

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.strict-module]
""")

        original_argv = sys.argv
        original_stderr = sys.stderr
        try:
            sys.stderr = io.StringIO()
            sys.argv = [
                "strict-module",
                str(test_file),
                "--baseline",
                str(baseline_file),
            ]
            result = main()
            stderr_output = sys.stderr.getvalue()
            assert result == 1
            assert stderr_output.strip() == ERR_BASELINE_MISSING.format(
                path=baseline_file
            )
        finally:
            sys.argv = original_argv
            sys.stderr = original_stderr

    def test_main_with_malformed_baseline_file(self, tmp_path):
        """Test main() with malformed baseline file."""
        baseline_file = tmp_path / "baseline.json"
        baseline_file.write_text("{ invalid json }")

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.strict-module]
""")

        original_argv = sys.argv
        original_stderr = sys.stderr
        try:
            sys.stderr = io.StringIO()
            sys.argv = [
                "strict-module",
                str(test_file),
                "--baseline",
                str(baseline_file),
            ]
            result = main()
            stderr_output = sys.stderr.getvalue()
            assert result == 1
            assert stderr_output.strip() == ERR_BASELINE_INVALID_JSON.format(
                path=baseline_file
            )
        finally:
            sys.argv = original_argv
            sys.stderr = original_stderr
