"""Tests for CLI functionality."""

import sys
from pathlib import Path

import pytest

from strict_module.cli import main

from strict_module.cli import main


class TestCli:
    """Test CLI functionality."""

    def test_cli_good_fixture(self, fixture_dir, monkeypatch, capsys, tmp_path):
        """Test CLI on good fixtures."""
        fixture_file = fixture_dir / "good" / "r001_good_basic.py"

        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
[tool.dto-strict]
service_paths = ["**/*.py"]
"""
        )

        monkeypatch.setattr(
            sys,
            "argv",
            ["dto-strict", str(fixture_file), "--config", str(config_file)],
        )

        exit_code = main()
        assert exit_code == 0

    def test_cli_bad_fixture(self, fixture_dir, monkeypatch, capsys, tmp_path):
        """Test CLI on bad fixtures."""
        fixture_file = fixture_dir / "bad" / "r001_bad_param.py"

        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
[tool.dto-strict]
service_paths = ["**/*.py"]
"""
        )

        monkeypatch.setattr(
            sys,
            "argv",
            ["dto-strict", str(fixture_file), "--config", str(config_file)],
        )

        exit_code = main()
        assert exit_code > 0

        captured = capsys.readouterr()
        assert "R001" in captured.out

    def test_cli_format_github(self, fixture_dir, monkeypatch, capsys, tmp_path):
        """Test CLI with GitHub format output."""
        fixture_file = fixture_dir / "bad" / "r001_bad_param.py"

        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
[tool.dto-strict]
service_paths = ["**/*.py"]
"""
        )

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "dto-strict",
                str(fixture_file),
                "--format",
                "github",
                "--config",
                str(config_file),
            ],
        )

        exit_code = main()
        assert exit_code > 0

        captured = capsys.readouterr()
        assert "::error" in captured.out or "::warning" in captured.out
