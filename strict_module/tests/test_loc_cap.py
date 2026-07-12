"""Tests for loc-cap subcommand."""

from strict_module.config import Config, LocCapConfig
from strict_module.loc_cap import LocCap


class TestCountLines:
    """Tests for count_lines function."""

    def test_count_lines_basic(self, tmp_path):
        """Count lines in a simple file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\n")
        assert LocCap.LocCap.count_lines(str(test_file)) == 3

    def test_count_lines_no_trailing_newline(self, tmp_path):
        """Count lines without trailing newline."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3")
        assert LocCap.LocCap.count_lines(str(test_file)) == 3

    def test_count_lines_empty_file(self, tmp_path):
        """Count lines in empty file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("")
        assert LocCap.LocCap.count_lines(str(test_file)) == 0

    def test_count_lines_nonexistent_file(self):
        """Count lines in nonexistent file returns 0."""
        assert LocCap.LocCap.count_lines("/nonexistent/file.py") == 0


class TestLoadBaseline:
    """Tests for load_baseline function."""

    def test_load_baseline_valid(self, tmp_path):
        """Load baseline from valid file."""
        baseline_file = tmp_path / "baseline.txt"
        baseline_file.write_text("path/to/file1.py:100\npath/to/file2.py:250\n")
        baseline = LocCap.LocCap.load_baseline(str(baseline_file))
        assert baseline["path/to/file1.py"] == 100
        assert baseline["path/to/file2.py"] == 250

    def test_load_baseline_with_empty_lines(self, tmp_path):
        """Load baseline skips empty lines."""
        baseline_file = tmp_path / "baseline.txt"
        baseline_file.write_text("path/to/file1.py:100\n\npath/to/file2.py:250\n")
        baseline = LocCap.LocCap.load_baseline(str(baseline_file))
        assert len(baseline) == 2
        assert baseline["path/to/file1.py"] == 100

    def test_load_baseline_missing_file(self, tmp_path):
        """Load baseline returns empty dict if file missing."""
        baseline = LocCap.LocCap.load_baseline(str(tmp_path / "nonexistent.txt"))
        assert baseline == {}

    def test_load_baseline_with_whitespace(self, tmp_path):
        """Load baseline handles whitespace in keys/values."""
        baseline_file = tmp_path / "baseline.txt"
        baseline_file.write_text("  path/to/file.py  :  500  \n")
        baseline = LocCap.LocCap.load_baseline(str(baseline_file))
        assert baseline["path/to/file.py"] == 500


class TestFindPythonFiles:
    """Tests for find_python_files function."""

    def test_find_python_files_basic(self, tmp_path):
        """Find Python files in directory."""
        (tmp_path / "file1.py").write_text("line1\nline2\n")
        (tmp_path / "file2.py").write_text("a\n")
        files = LocCap.LocCap.find_python_files(str(tmp_path))
        assert len(files) == 2
        assert files[str(tmp_path / "file1.py")] == 2
        assert files[str(tmp_path / "file2.py")] == 1

    def test_find_python_files_excludes_migrations(self, tmp_path):
        """Find Python files excludes migrations."""
        (tmp_path / "file.py").write_text("a\n")
        migrations_dir = tmp_path / "migrations"
        migrations_dir.mkdir()
        (migrations_dir / "0001_initial.py").write_text("a\nb\n")
        files = LocCap.LocCap.find_python_files(str(tmp_path))
        assert len(files) == 1
        assert str(tmp_path / "file.py") in files

    def test_find_python_files_excludes_management_commands(self, tmp_path):
        """Find Python files excludes management commands."""
        (tmp_path / "file.py").write_text("a\n")
        mgmt_dir = tmp_path / "management" / "commands"
        mgmt_dir.mkdir(parents=True)
        (mgmt_dir / "cmd.py").write_text("a\nb\n")
        files = LocCap.LocCap.find_python_files(str(tmp_path))
        assert len(files) == 1
        assert str(tmp_path / "file.py") in files

    def test_find_python_files_nested(self, tmp_path):
        """Find Python files in nested directories."""
        app_dir = tmp_path / "app"
        app_dir.mkdir()
        (app_dir / "models.py").write_text("a\n")
        sub_dir = app_dir / "sub"
        sub_dir.mkdir()
        (sub_dir / "file.py").write_text("x\ny\n")
        files = LocCap.LocCap.find_python_files(str(tmp_path))
        assert len(files) == 2

    def test_find_python_files_nonexistent_path(self):
        """Find Python files returns empty dict for nonexistent path."""
        files = LocCap.LocCap.find_python_files("/nonexistent/path")
        assert files == {}


class TestGenerateBaseline:
    """Tests for generate_baseline function."""

    def test_generate_baseline_basic(self, tmp_path):
        """Generate baseline output."""
        (tmp_path / "file1.py").write_text("a\n" * 100)
        (tmp_path / "file2.py").write_text("b\n" * 50)
        output = LocCap.LocCap.generate_baseline(str(tmp_path))
        lines = output.strip().split("\n")
        assert len(lines) == 2
        # Should be sorted by LOC descending
        assert "100" in lines[0]  # file1 is first (higher LOC)
        assert "50" in lines[1]  # file2 is second (lower LOC)

    def test_generate_baseline_with_floor(self, tmp_path):
        """Generate baseline respects floor parameter."""
        (tmp_path / "file1.py").write_text("a\n" * 600)
        (tmp_path / "file2.py").write_text("b\n" * 100)
        output = LocCap.LocCap.generate_baseline(str(tmp_path), floor=200)
        assert "file1.py" in output
        assert "file2.py" not in output

    def test_generate_baseline_format(self, tmp_path):
        """Generate baseline output format is path:loc."""
        (tmp_path / "test.py").write_text("line1\nline2\nline3\n")
        output = LocCap.LocCap.generate_baseline(str(tmp_path))
        assert "test.py:3" in output


class TestRunLocCap:
    """Tests for run_loc_cap function."""

    def test_run_loc_cap_all_pass(self, tmp_path):
        """All files under cap returns 0."""
        (tmp_path / "file1.py").write_text("a\n" * 100)
        (tmp_path / "file2.py").write_text("b\n" * 200)
        exit_code = LocCap.LocCap.run_loc_cap(str(tmp_path), hard_cap=694, soft_target=500)
        assert exit_code == 0

    def test_run_loc_cap_new_offender(self, tmp_path, capsys):
        """New file over cap returns 1."""
        (tmp_path / "file.py").write_text("a\n" * 700)
        exit_code = LocCap.LocCap.run_loc_cap(str(tmp_path), hard_cap=694, soft_target=500)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "NEW OFFENDER" in captured.out

    def test_run_loc_cap_baselined_at_cap(self, tmp_path):
        """Baselined file at exactly baseline passes."""
        baseline_file = tmp_path / "baseline.txt"
        baseline_file.write_text(f"{tmp_path}/file.py:700\n")

        (tmp_path / "file.py").write_text("a\n" * 700)
        exit_code = LocCap.LocCap.run_loc_cap(
            str(tmp_path),
            hard_cap=694,
            soft_target=500,
            baseline_file=str(baseline_file),
        )
        assert exit_code == 0

    def test_run_loc_cap_baselined_file_grew(self, tmp_path, capsys):
        """Baselined file that grew returns 1."""
        baseline_file = tmp_path / "baseline.txt"
        baseline_file.write_text(f"{tmp_path}/file.py:700\n")

        (tmp_path / "file.py").write_text("a\n" * 750)  # Grew from 700 to 750
        exit_code = LocCap.LocCap.run_loc_cap(
            str(tmp_path),
            hard_cap=694,
            soft_target=500,
            baseline_file=str(baseline_file),
        )
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "grew by" in captured.out

    def test_run_loc_cap_soft_warning(self, tmp_path, capsys):
        """Files in soft target range produce warning."""
        (tmp_path / "file.py").write_text("a\n" * 600)
        exit_code = LocCap.LocCap.run_loc_cap(str(tmp_path), hard_cap=694, soft_target=500)
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "soft target" in captured.out

    def test_run_loc_cap_improvement(self, tmp_path, capsys):
        """File that improved (dropped below cap) is noted."""
        baseline_file = tmp_path / "baseline.txt"
        baseline_file.write_text(f"{tmp_path}/file.py:700\n")

        (tmp_path / "file.py").write_text("a\n" * 600)  # Improved from 700 to 600
        exit_code = LocCap.LocCap.run_loc_cap(
            str(tmp_path),
            hard_cap=694,
            soft_target=500,
            baseline_file=str(baseline_file),
        )
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "improved" in captured.out

    def test_run_loc_cap_LocCap.generate_baseline(self, tmp_path, capsys):
        """Generate mode outputs baseline format."""
        (tmp_path / "file1.py").write_text("a\n" * 100)
        (tmp_path / "file2.py").write_text("b\n" * 50)
        exit_code = LocCap.LocCap.run_loc_cap(str(tmp_path), generate=True)
        assert exit_code == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 2
        assert "file1.py:100" in captured.out
        assert "file2.py:50" in captured.out

    def test_run_loc_cap_custom_hard_cap(self, tmp_path):
        """Custom hard cap is respected."""
        (tmp_path / "file.py").write_text("a\n" * 200)
        exit_code = LocCap.LocCap.run_loc_cap(str(tmp_path), hard_cap=150, soft_target=100)
        assert exit_code == 1


class TestLocCapConfig:
    """Tests for LocCapConfig dataclass."""

    def test_loc_cap_config_defaults(self):
        """LocCapConfig has correct defaults."""
        config = LocCapConfig()
        assert config.hard_cap == 694
        assert config.soft_target == 500
        assert config.baseline_file == ".loc-cap-baseline.txt"

    def test_loc_cap_config_custom_values(self):
        """LocCapConfig accepts custom values."""
        config = LocCapConfig(hard_cap=500, soft_target=300, baseline_file="custom.txt")
        assert config.hard_cap == 500
        assert config.soft_target == 300
        assert config.baseline_file == "custom.txt"


class TestConfigLocCapLoading:
    """Tests for loc-cap config loading from pyproject."""

    def test_config_loads_loc_cap_defaults(self, tmp_path):
        """Config loads loc-cap defaults."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[tool.dto-strict]
service_paths = ["apps/*/services/*.py"]
"""
        )
        config = Config.from_pyproject(pyproject)
        assert config.loc_cap.hard_cap == 694
        assert config.loc_cap.soft_target == 500
        assert config.loc_cap.baseline_file == ".loc-cap-baseline.txt"

    def test_config_loads_loc_cap_custom(self, tmp_path):
        """Config loads custom loc-cap settings."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[tool.dto-strict.loc-cap]
hard_cap = 500
soft_target = 300
baseline_file = "custom_baseline.txt"
"""
        )
        config = Config.from_pyproject(pyproject)
        assert config.loc_cap.hard_cap == 500
        assert config.loc_cap.soft_target == 300
        assert config.loc_cap.baseline_file == "custom_baseline.txt"
