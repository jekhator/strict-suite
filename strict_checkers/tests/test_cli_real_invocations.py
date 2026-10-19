"""Tests for CLI with real subprocess invocations."""

import json
import subprocess
import sys


class TestCLIRealInvocations:
    """Test CLI with real subprocess invocations."""

    def test_cli_lint_text_format(self, project_dir):
        """Test CLI linting with text output format."""
        bad_file = project_dir / "apps" / "services" / "bad.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                str(bad_file),
                "--format",
                "text",
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "R006" in result.stdout
        assert "bad.py" in result.stdout

    def test_cli_lint_json_format(self, project_dir):
        """Test CLI linting with JSON output format."""
        bad_file = project_dir / "apps" / "services" / "bad.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                str(bad_file),
                "--format",
                "json",
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert isinstance(data, (dict, list))
        if isinstance(data, list):
            assert len(data) == 2
            assert "rule_id" in data[0]
        else:
            assert any(
                v["rule_id"] in ["R001", "R006"] for v in data.get("violations", [])
            )

    def test_cli_lint_github_format(self, project_dir):
        """Test CLI linting with GitHub Actions output format."""
        bad_file = project_dir / "apps" / "services" / "bad.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                str(bad_file),
                "--format",
                "github",
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "::error" in result.stdout

    def test_cli_lint_clean_file(self, project_dir):
        """Test CLI linting clean file exits with 0."""
        good_file = project_dir / "apps" / "services" / "good.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                str(good_file),
                "--format",
                "text",
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_cli_generate_baseline(self, project_dir):
        """Test CLI baseline generation."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                str(project_dir),
                "--generate-baseline",
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert sorted(entry["rule_id"] for entry in data) == ["R006", "R009"]

    def test_cli_with_baseline(self, project_dir):
        """Test CLI with baseline file."""
        baseline_file = project_dir / ".strict-module-baseline.json"
        bad_file = project_dir / "apps" / "services" / "bad.py"

        gen_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                str(bad_file),
                "--generate-baseline",
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        baseline_file.write_text(gen_result.stdout)

        lint_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                str(bad_file),
                "--baseline",
                str(baseline_file),
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert lint_result.returncode == 0

    def test_cli_loc_cap_help(self, project_dir):
        """Test loc-cap subcommand basic invocation."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                "loc-cap",
                str(project_dir),
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_cli_missing_path_error(self, project_dir):
        """Test CLI error when path is missing."""
        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "error: PATH argument required" in result.stderr


class TestCLILocCap:
    """Test loc-cap subcommand with real invocations."""

    def test_loc_cap_generate_baseline(self, project_dir):
        """Test loc-cap baseline generation."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                "loc-cap",
                str(project_dir),
                "--generate-baseline",
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            if line.strip():
                assert ":" in line

    def test_loc_cap_with_custom_limits(self, project_dir):
        """Test loc-cap with custom hard and soft limits."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                "loc-cap",
                str(project_dir),
                "--hard-cap",
                "50",
                "--soft-target",
                "30",
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_loc_cap_with_baseline(self, project_dir):
        """Test loc-cap with baseline file."""
        baseline_file = project_dir / ".loc-cap-baseline.txt"
        baseline_file.write_text("apps/services/bad.py: 100\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "strict_module.cli",
                "loc-cap",
                str(project_dir),
                "--baseline",
                str(baseline_file),
            ],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
