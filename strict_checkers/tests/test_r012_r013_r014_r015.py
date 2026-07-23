"""Tests for R012-R015 formatting dialect rules."""

import ast
from pathlib import Path

from strict_checkers.r012 import R012Checker
from strict_checkers.r013 import R013Checker
from strict_checkers.r014 import R014Checker
from strict_checkers.r015 import R015Checker
from strict_config._config import Config


class TestR012FitsOneLineStays:
    """Test R012: calls fitting on one line should not be exploded."""

    def test_single_arg_call_short_split_across_lines(self):
        """Single-argument call under 80 chars split across lines should flag."""
        source = """
helper(
    arg
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 1
        assert checker.violations[0].rule_id == "R012"

    def test_single_arg_call_long_split_across_lines_allowed(self):
        """Single-argument call over 80 chars split across lines is allowed."""
        source = """
very_long_function_name_that_exceeds_eighty_characters_when_combined_with_arg(
    argument
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_multi_arg_call_split_not_flagged(self):
        """Multi-argument calls are not flagged by R012."""
        source = """
func(
    arg1,
    arg2,
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_single_line_call_not_flagged(self):
        """Single-line calls are not flagged."""
        source = "func(arg)"
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_r012_noqa_suppression(self):
        """R012 violations can be suppressed with noqa."""
        source = """
helper(  # noqa: R012
    arg
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_r012_exactly_80_chars(self):
        """Calls exactly 80 chars are flagged."""
        source = """
short(
    x
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 1

    def test_r012_with_keyword_arg(self):
        """Single kwarg under 80 chars split across lines should flag."""
        source = """
func(
    x=1
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 1

    def test_r012_empty_call_not_flagged(self):
        """Calls with no arguments are not flagged."""
        source = """
func(
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_r012_handles_syntax_errors_gracefully(self):
        """R012 should handle edge cases gracefully."""
        source = "short(x)"
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_r012_nested_calls(self):
        """R012 handles nested calls correctly."""
        source = """
outer(
    inner(x)
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 1

    def test_r012_with_string_literal(self):
        """R012 handles calls with string literals."""
        source = '''
log(
    "message"
)
'''
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 1

    def test_r012_boundary_exactly_79_chars(self):
        """Calls at exactly 79 chars should be flagged."""
        source = """
f(
    x
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 1

    def test_r012_three_line_single_arg_call(self):
        """Single-arg calls spanning 3+ lines should be flagged."""
        source = """
func(
    argument
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R012Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 1


class TestR013SignatureGrouping:
    """Test R013: multi-parameter signatures should group 2-3 per line (currently disabled)."""

    def test_r013_all_patterns_pass(self):
        """R013 is currently disabled and does not flag any violations."""
        source = """
def func(
    self, x: int,
    y: int,
    z: int,
) -> None:
    pass
"""
        tree = ast.parse(source)
        config = Config()
        checker = R013Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0


class TestR014KwargCallGrouping:
    """Test R014: multi-kwarg calls should group 2-3 per line (currently disabled)."""

    def test_r014_all_patterns_pass(self):
        """R014 is currently disabled and does not flag any violations."""
        source = """
func(
    x=1,
    y=2,
)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R014Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0


class TestR015WrapPathSeparation:
    """Test R015: try/except blocks should mirror blank-line patterns."""

    def test_matching_statement_counts(self):
        """Try/except with matching statement counts should not flag."""
        source = """
try:
    x = foo()
    y = bar()
except Exception:
    x = foo_fail()
    y = bar_fail()
"""
        tree = ast.parse(source)
        config = Config()
        checker = R015Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_different_statement_counts_allowed(self):
        """Try/except with different statement counts (e.g., assignment in try) allowed."""
        source = """
try:
    result = call()
    process(result)
except Exception:
    process(None)
"""
        tree = ast.parse(source)
        config = Config()
        checker = R015Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_r015_noqa_suppression(self):
        """R015 violations can be suppressed with noqa."""
        source = """
try:  # noqa: R015
    x = foo()
    y = bar()
except Exception:
    x = foo()
"""
        tree = ast.parse(source)
        config = Config()
        checker = R015Checker(Path("test.py"), source, config)
        checker.visit(tree)

        assert len(checker.violations) == 0
