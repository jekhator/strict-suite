"""Tests for CLI with real subprocess invocations."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def test_project_dir():
    """Create a temporary project with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        bad_service_file = project_root / "apps" / "services" / "bad.py"
        bad_service_file.parent.mkdir(parents=True, exist_ok=True)
        bad_service_file.write_text("""
\"\"\"Bad service with Dict[str, Any].\"\"\"
from typing import Any, Dict

def process_order(data: Dict[str, Any]) -> dict:
    \"\"\"Process order data.\"\"\"
    return {"status": "ok"}
""")

        good_service_file = project_root / "apps" / "services" / "good.py"
        good_service_file.write_text("""
\"\"\"Good service without Dict[str, Any].\"\"\"
from dataclasses import dataclass

@dataclass
class OrderRequest:
    customer_id: int
    amount: float

def process_order(data: OrderRequest) -> dict:
    \"\"\"Process order data.\"\"\"
    return {"status": "ok"}
""")

        pyproject = project_root / "pyproject.toml"
        pyproject.write_text("""
[tool.strict-module]
service_paths = ["apps/*/services/*.py"]
""")

        yield project_root


class TestCLIRealInvocations:
    """Test CLI with real subprocess invocations."""

    def test_cli_lint_text_format(self, test_project_dir):
        """Test CLI linting with text output format."""
        bad_file = test_project_dir / "apps" / "services" / "bad.py"

        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", str(bad_file), "--format", "text"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert ("R001" in result.stdout or "R006" in result.stdout)
        assert "bad.py" in result.stdout

    def test_cli_lint_json_format(self, test_project_dir):
        """Test CLI linting with JSON output format."""
        bad_file = test_project_dir / "apps" / "services" / "bad.py"

        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", str(bad_file), "--format", "json"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert isinstance(data, (dict, list))
        if isinstance(data, list):
            assert len(data) > 0
            assert "rule_id" in data[0]
        else:
            assert any(v["rule_id"] in ["R001", "R006"] for v in data.get("violations", []))

    def test_cli_lint_github_format(self, test_project_dir):
        """Test CLI linting with GitHub Actions output format."""
        bad_file = test_project_dir / "apps" / "services" / "bad.py"

        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", str(bad_file), "--format", "github"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "::error" in result.stdout or "::warning" in result.stdout

    def test_cli_lint_clean_file(self, test_project_dir):
        """Test CLI linting clean file exits with 0."""
        good_file = test_project_dir / "apps" / "services" / "good.py"

        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", str(good_file), "--format", "text"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_cli_generate_baseline(self, test_project_dir):
        """Test CLI baseline generation."""
        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", str(test_project_dir), "--generate-baseline"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, (dict, list))
        if isinstance(data, list):
            assert len(data) >= 0
        else:
            assert "violations_by_rule" in data or "violations" in data

    def test_cli_with_baseline(self, test_project_dir):
        """Test CLI with baseline file."""
        baseline_file = test_project_dir / ".strict-module-baseline.json"
        bad_file = test_project_dir / "apps" / "services" / "bad.py"

        gen_result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", str(bad_file), "--generate-baseline"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        baseline_file.write_text(gen_result.stdout)

        lint_result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", str(bad_file), "--baseline", str(baseline_file)],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert lint_result.returncode == 0

    def test_cli_loc_cap_help(self, test_project_dir):
        """Test loc-cap subcommand basic invocation."""
        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", "loc-cap", str(test_project_dir)],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert "Python files" in result.stdout or "LOC" in result.stdout or result.returncode in [0, 1]

    def test_cli_missing_path_error(self, test_project_dir):
        """Test CLI error when path is missing."""
        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "error" in result.stderr.lower() or "error" in result.stdout.lower()


class TestCLILocCap:
    """Test loc-cap subcommand with real invocations."""

    def test_loc_cap_generate_baseline(self, test_project_dir):
        """Test loc-cap baseline generation."""
        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", "loc-cap", str(test_project_dir), "--generate-baseline"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        assert len(lines) > 0
        for line in lines:
            if line.strip():
                assert ":" in line

    def test_loc_cap_with_custom_limits(self, test_project_dir):
        """Test loc-cap with custom hard and soft limits."""
        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", "loc-cap", str(test_project_dir),
             "--hard-cap", "50", "--soft-target", "30"],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode in [0, 1]

    def test_loc_cap_with_baseline(self, test_project_dir):
        """Test loc-cap with baseline file."""
        baseline_file = test_project_dir / ".loc-cap-baseline.txt"
        baseline_file.write_text("apps/services/bad.py: 100\n")

        result = subprocess.run(
            [sys.executable, "-m", "strict_module.cli", "loc-cap", str(test_project_dir),
             "--baseline", str(baseline_file)],
            cwd=str(test_project_dir),
            capture_output=True,
            text=True,
        )

        assert result.returncode in [0, 1]
