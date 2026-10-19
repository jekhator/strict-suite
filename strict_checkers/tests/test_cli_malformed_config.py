"""Tests for the CLI reaction to an invalid pyproject.toml."""


class TestCliMalformedConfig:
    """Test suite for the CLI reaction to an invalid pyproject.toml."""

    def test_malformed_config_exits_blocking_with_message(self, tmp_path, monkeypatch, capsys):
        """The CLI prints the config error to stderr and exits with the blocking code."""
        from strict_config import constants as const
        from strict_module.cli import main

        path = tmp_path / "pyproject.toml"
        path.write_text("[tool.strict-module\n")
        monkeypatch.setattr(
            "sys.argv",
            ["strict-module", "--config", str(path), str(tmp_path)],
        )

        exit_code = main()
        captured = capsys.readouterr()

        assert exit_code == const.EXIT_CODE_HIGH_VIOLATION
        assert str(path) in captured.err
