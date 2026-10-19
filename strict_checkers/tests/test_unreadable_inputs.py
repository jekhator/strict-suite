"""Tests that unreadable or unparseable inputs fail the run instead of passing silently."""

import pytest

from strict_config import constants as const
from strict_config._config import Config
from strict_linter import DtoStrictLinter, LintInputError

UNDECODABLE_BYTES = b"\x80\x81\x82\x83"


class TestUnreadableInputs:
    """Unreadable and unparseable inputs produce an error line and exit 1."""

    def test_lint_path_raises_for_undecodable_file_in_directory(self, tmp_path):
        """A directory walk raises LintInputError when one member cannot be decoded."""
        (tmp_path / "bad.py").write_bytes(UNDECODABLE_BYTES)
        linter = DtoStrictLinter(Config())

        with pytest.raises(LintInputError, match="cannot read Python source"):
            linter.lint_path(tmp_path)

    def test_cli_undecodable_file_exits_one_with_stderr_error(self, tmp_path, monkeypatch, run_cli):
        """The linter exits 1 and names the unreadable file on stderr."""
        source = tmp_path / "undecodable.py"
        source.write_bytes(UNDECODABLE_BYTES)
        monkeypatch.chdir(tmp_path)

        code, out, err = run_cli([str(source)])

        assert code == const.EXIT_CODE_HIGH_VIOLATION
        assert "cannot read Python source" in err
        assert str(source) in err
        assert out == ""

    def test_cli_syntax_error_file_exits_one_with_stderr_error(self, tmp_path, monkeypatch, run_cli):
        """The linter exits 1 when a file cannot be parsed, instead of reporting it clean."""
        source = tmp_path / "broken.py"
        source.write_text("def broken(:\n")
        monkeypatch.chdir(tmp_path)

        code, out, err = run_cli([str(source)])

        assert code == const.EXIT_CODE_HIGH_VIOLATION
        assert "cannot parse Python source" in err
        assert out == ""

    def test_cli_generate_baseline_with_syntax_error_exits_one(self, tmp_path, monkeypatch, run_cli):
        """Baseline generation refuses to write a baseline from an unparseable file."""
        source = tmp_path / "broken.py"
        source.write_text("def broken(:\n")
        monkeypatch.chdir(tmp_path)

        code, out, err = run_cli(["--generate-baseline", str(source)])

        assert code == const.EXIT_CODE_HIGH_VIOLATION
        assert "cannot parse Python source" in err
        assert out == ""

    def test_loc_cap_undecodable_file_exits_one(self, tmp_path, run_cli):
        """The LOC cap exits 1 when a counted file cannot be decoded."""
        (tmp_path / "module.py").write_bytes(UNDECODABLE_BYTES)
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[tool.strict-module]\nservice_paths = ["**/*.py"]\n')

        code, out, err = run_cli(["loc-cap", str(tmp_path), "--config", str(pyproject)])

        assert code == const.EXIT_CODE_HIGH_VIOLATION
        assert "cannot read file for LOC count" in err
        assert out == ""

    def test_loc_cap_unreadable_baseline_exits_one(self, tmp_path, run_cli):
        """The LOC cap exits 1 when the baseline file exists but cannot be decoded."""
        (tmp_path / "module.py").write_text("x = 1\n")
        baseline = tmp_path / "baseline.txt"
        baseline.write_bytes(UNDECODABLE_BYTES)
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[tool.strict-module]\nservice_paths = ["**/*.py"]\n')

        code, out, err = run_cli(
            ["loc-cap", str(tmp_path), "--config", str(pyproject), "--baseline", str(baseline)]
        )

        assert code == const.EXIT_CODE_HIGH_VIOLATION
        assert "LOC cap baseline cannot be read" in err
        assert out == ""
