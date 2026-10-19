"""Tests that R012 ignores calls whose only argument is itself multi-line."""

import ast
from pathlib import Path

from strict_checkers.r012 import R012Checker


class TestR012MultilineArgument:
    """A call is collapsible only when its single argument fits on one line."""

    def test_multiline_string_argument_is_not_flagged(self, fixture_dir, config):
        """A single-argument call whose argument is a multi-line string produces no R012 finding."""
        source = (fixture_dir / "good" / "r012_multiline_string_argument.py").read_text()
        checker = R012Checker(Path("payload.py"), source, config)
        checker.visit(ast.parse(source))

        assert checker.violations == []

    def test_genuinely_split_short_call_is_still_flagged(self, fixture_dir, config):
        """A short single-argument call split across lines is still reported as R012."""
        source = (fixture_dir / "bad" / "r012_bad_split_short_call.py").read_text()
        checker = R012Checker(Path("value.py"), source, config)
        checker.visit(ast.parse(source))

        assert len(checker.violations) == 1
        assert checker.violations[0].rule_id == "R012"
        assert checker.violations[0].line == 3

    def test_keyword_argument_spanning_lines_is_not_flagged(self, config):
        """A single keyword argument whose value is a multi-line string is not flagged."""
        source = 'value = dict(\n    text="""\nabc\n""")\n'
        checker = R012Checker(Path("kw.py"), source, config)
        checker.visit(ast.parse(source))

        assert checker.violations == []
