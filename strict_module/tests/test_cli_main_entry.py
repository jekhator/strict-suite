"""Tests for CLI main() entry point with direct calls."""

import sys

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
        baseline_file = tmp_path / "baseline.json"
        baseline_file.write_text('{"violations": []}')

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.strict-module]
""")

        original_argv = sys.argv
        try:
            sys.argv = [
                "strict-module",
                str(test_file),
                "--baseline",
                str(baseline_file),
            ]
            result = main()
            assert result == 0
        finally:
            sys.argv = original_argv
