"""Tests for CLI functionality."""

import sys

from strict_config.constants import ERR_NONEXISTENT_PATH
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

    def test_cli_nonexistent_path(self, monkeypatch, capsys, tmp_path):
        """Test CLI errors on nonexistent path."""
        nonexistent_path = "/tmp/does-not-exist-xyz-12345"

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
            ["dto-strict", nonexistent_path, "--config", str(config_file)],
        )

        exit_code = main()
        assert exit_code != 0

        captured = capsys.readouterr()
        expected_msg = ERR_NONEXISTENT_PATH.format(path=nonexistent_path)
        assert expected_msg in captured.err
