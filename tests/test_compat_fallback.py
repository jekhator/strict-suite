"""Tests for backward compatibility fallbacks (0.5.0+)."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from strict_module.config import Config
from strict_module.loc_cap import load_baseline


def test_config_reads_strict_module_first():
    """Config: [tool.strict-module] takes precedence over [tool.dto-strict]."""
    with TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "pyproject.toml"
        config_path.write_text("""
[tool.strict-module]
service_paths = ["new/path/*.py"]
disabled_rules = ["R001"]

[tool.dto-strict]
service_paths = ["old/path/*.py"]
disabled_rules = ["R002"]
""")
        config = Config.from_pyproject(config_path)
        assert config.service_paths == ["new/path/*.py"]
        assert config.disabled_rules == ["R001"]


def test_config_falls_back_to_dto_strict():
    """Config: Falls back to [tool.dto-strict] if [tool.strict-module] absent."""
    with TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "pyproject.toml"
        config_path.write_text("""
[tool.dto-strict]
service_paths = ["fallback/path/*.py"]
disabled_rules = ["R003"]
""")
        config = Config.from_pyproject(config_path)
        assert config.service_paths == ["fallback/path/*.py"]
        assert config.disabled_rules == ["R003"]


def test_config_uses_defaults_when_no_sections():
    """Config: Uses defaults if no config sections present."""
    with TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "pyproject.toml"
        config_path.write_text("[build-system]\nrequires = []")
        config = Config.from_pyproject(config_path)
        assert config.service_paths == ["apps/*/services/*.py", "**/services/*.py"]
        assert config.disabled_rules == []


def test_baseline_prefers_strict_module_file():
    """Baseline: Prefers .strict-module-baseline.txt over .dto-strict-baseline.txt."""
    with TemporaryDirectory() as tmpdir:
        strict_baseline = Path(tmpdir) / ".strict-module-baseline.txt"
        dto_baseline = Path(tmpdir) / ".dto-strict-baseline.txt"

        strict_baseline.write_text("file1.py:100\n")
        dto_baseline.write_text("file2.py:200\n")

        old_cwd = Path.cwd()
        try:
            os.chdir(tmpdir)
            baseline = load_baseline(".loc-cap-baseline.txt")
            assert "file1.py" in baseline
            assert baseline["file1.py"] == 100
            assert "file2.py" not in baseline
        finally:
            os.chdir(old_cwd)


def test_baseline_falls_back_to_dto_strict_file():
    """Baseline: Falls back to .dto-strict-baseline.txt if .strict-module absent."""
    with TemporaryDirectory() as tmpdir:
        dto_baseline = Path(tmpdir) / ".dto-strict-baseline.txt"
        dto_baseline.write_text("file3.py:300\n")

        old_cwd = Path.cwd()
        try:
            os.chdir(tmpdir)
            baseline = load_baseline(".loc-cap-baseline.txt")
            assert "file3.py" in baseline
            assert baseline["file3.py"] == 300
        finally:
            os.chdir(old_cwd)


def test_baseline_returns_empty_when_no_files_exist():
    """Baseline: Returns empty dict if no baseline files exist."""
    with TemporaryDirectory() as tmpdir:
        old_cwd = Path.cwd()
        try:
            os.chdir(tmpdir)
            baseline = load_baseline(".loc-cap-baseline.txt")
            assert baseline == {}
        finally:
            os.chdir(old_cwd)
