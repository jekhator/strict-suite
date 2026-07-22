"""Test R002 noqa suppression with various dash formats and multi-line dicts."""

import json
import subprocess
import sys
import textwrap
from pathlib import Path
from tempfile import TemporaryDirectory


class TestNoqaR002:
    """Test suite for related functionality."""

    def test_r002_noqa_trailing_hyphen(self):
        """R002 violation with trailing noqa on same line as dict opening."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "services" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                textwrap.dedent("""
                def fn():
                    return {"a": 1, "b": 2, "c": 3}  # noqa: dto-strict-R002 - explanation
            """)
            )
            config = Path(tmpdir) / "pyproject.toml"
            config.write_text(
                textwrap.dedent("""
                [tool.dto-strict]
                service_paths = ["services/*.py"]
            """)
            )

            result = subprocess.run(
                [sys.executable, "-m", "strict_module.cli", ".", "--format", "json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Should have no R002 violations
            violations = json.loads(result.stdout)
            r002_violations = [v for v in violations if v["rule_id"] == "R002"]
            assert len(r002_violations) == 0, (
                f"Expected 0 R002, got {len(r002_violations)}"
            )

    def test_r002_noqa_trailing_emdash(self):
        """R002 violation with trailing noqa using em-dash (—)."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "services" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                textwrap.dedent("""
                def fn():
                    return {"a": 1, "b": 2, "c": 3}  # noqa: dto-strict-R002 — explanation
            """)
            )
            config = Path(tmpdir) / "pyproject.toml"
            config.write_text(
                textwrap.dedent("""
                [tool.dto-strict]
                service_paths = ["services/*.py"]
            """)
            )

            result = subprocess.run(
                [sys.executable, "-m", "strict_module.cli", ".", "--format", "json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Should have no R002 violations
            violations = json.loads(result.stdout)
            r002_violations = [v for v in violations if v["rule_id"] == "R002"]
            assert len(r002_violations) == 0, (
                f"Expected 0 R002, got {len(r002_violations)}"
            )

    def test_r002_noqa_opening_brace_emdash(self):
        """R002 violation with noqa on opening-brace line (multi-line dict) using em-dash."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "services" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                textwrap.dedent("""
                def fn():
                    return {  # noqa: dto-strict-R002 — opening-brace
                        "a": 1,
                        "b": 2,
                        "c": 3,
                    }
            """)
            )
            config = Path(tmpdir) / "pyproject.toml"
            config.write_text(
                textwrap.dedent("""
                [tool.dto-strict]
                service_paths = ["services/*.py"]
            """)
            )

            result = subprocess.run(
                [sys.executable, "-m", "strict_module.cli", ".", "--format", "json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Should have no R002 violations
            violations = json.loads(result.stdout)
            r002_violations = [v for v in violations if v["rule_id"] == "R002"]
            assert len(r002_violations) == 0, (
                f"Expected 0 R002, got {len(r002_violations)}"
            )

    def test_r002_no_noqa_flagged(self):
        """R002 violation without noqa should be flagged."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "services" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                textwrap.dedent("""
                def fn():
                    return {"a": 1, "b": 2, "c": 3}
            """)
            )
            config = Path(tmpdir) / "pyproject.toml"
            config.write_text(
                textwrap.dedent("""
                [tool.dto-strict]
                service_paths = ["services/*.py"]
            """)
            )

            result = subprocess.run(
                [sys.executable, "-m", "strict_module.cli", ".", "--format", "json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Should have exactly 1 R002 violation
            violations = json.loads(result.stdout)
            r002_violations = [v for v in violations if v["rule_id"] == "R002"]
            assert len(r002_violations) == 1, (
                f"Expected 1 R002, got {len(r002_violations)}"
            )

    def test_r002_noqa_wrong_rule_not_suppressed(self):
        """R002 violation with noqa for different rule should NOT be suppressed."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "services" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                textwrap.dedent("""
                def fn():
                    return {"a": 1, "b": 2, "c": 3}  # noqa: dto-strict-R001
            """)
            )
            config = Path(tmpdir) / "pyproject.toml"
            config.write_text(
                textwrap.dedent("""
                [tool.dto-strict]
                service_paths = ["services/*.py"]
            """)
            )

            result = subprocess.run(
                [sys.executable, "-m", "strict_module.cli", ".", "--format", "json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Should have exactly 1 R002 violation (noqa is for R001, not R002)
            violations = json.loads(result.stdout)
            r002_violations = [v for v in violations if v["rule_id"] == "R002"]
            assert len(r002_violations) == 1, (
                f"Expected 1 R002, got {len(r002_violations)}"
            )

    def test_r002_bare_noqa_suppresses(self):
        """Bare `# noqa` should suppress R002."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "services" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                textwrap.dedent("""
                def fn():
                    return {"a": 1, "b": 2, "c": 3}  # noqa
            """)
            )
            config = Path(tmpdir) / "pyproject.toml"
            config.write_text(
                textwrap.dedent("""
                [tool.dto-strict]
                service_paths = ["services/*.py"]
            """)
            )

            result = subprocess.run(
                [sys.executable, "-m", "strict_module.cli", ".", "--format", "json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Should have no R002 violations
            violations = json.loads(result.stdout)
            r002_violations = [v for v in violations if v["rule_id"] == "R002"]
            assert len(r002_violations) == 0, (
                f"Expected 0 R002, got {len(r002_violations)}"
            )

    def test_r002_noqa_before_line_not_suppressed(self):
        """R002 with noqa on line BEFORE the violation should NOT suppress (multi-line only)."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "services" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                textwrap.dedent("""
                def fn():
                    x = 1  # noqa: dto-strict-R002
                    return {
                        "a": 1, "b": 2, "c": 3,
                    }
            """)
            )
            config = Path(tmpdir) / "pyproject.toml"
            config.write_text(
                textwrap.dedent("""
                [tool.dto-strict]
                service_paths = ["services/*.py"]
            """)
            )

            result = subprocess.run(
                [sys.executable, "-m", "strict_module.cli", ".", "--format", "json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Should have exactly 1 R002 violation
            # (noqa on line above the dict doesn't suppress)
            violations = json.loads(result.stdout)
            r002_violations = [v for v in violations if v["rule_id"] == "R002"]
            assert len(r002_violations) == 1, (
                f"Expected 1 R002, got {len(r002_violations)}"
            )
