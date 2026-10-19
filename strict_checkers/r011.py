"""Checker for R011: String literal at raise site."""

import ast
from pathlib import Path

from strict_checkers.base import BaseChecker
from strict_inspection import PathClassifier
from strict_rules import RuleSeverity

CONSTANTS_BASENAME = "constants.py"
CONSTANTS_SUFFIX = "_const.py"
CONSTANTS_DIRECTORY = "constants"


class R011Checker(BaseChecker):
    """Check for string literals in raise exception arguments.

    Enforces that exception message arguments must be references to ERR_*
    constants (via const.* or similar), never inline string literals or
    f-strings.
    """

    def visit_Raise(self, node: ast.Raise) -> None:
        """Visit raise statements to find string literal messages."""
        exc = node.exc
        if (
            isinstance(exc, ast.Call)
            and not PathClassifier.is_test_file(self.file_path)
            and not self._is_constant_module(self.file_path)
            and not self.is_suppressed(node, "R011")
            and self._has_string_literal(exc)
        ):
            self.add_violation(
                rule_id="R011",
                severity=RuleSeverity.HIGH,
                line=node.lineno,
                col=node.col_offset,
                message="String literal found in raise statement. Extract to constants/<feature>.py as ERR_<DOMAIN>_<CONDITION>, reference via const.",
            )

        self.generic_visit(node)

    @staticmethod
    def _is_constant_module(file_path: Path) -> bool:
        """Check if the file is a constants module (constants.py, *_const.py, or under a constants directory)."""
        return (
            file_path.name == CONSTANTS_BASENAME
            or file_path.name.endswith(CONSTANTS_SUFFIX)
            or CONSTANTS_DIRECTORY in file_path.parts
        )

    def _has_string_literal(self, call_node: ast.Call) -> bool:
        """Check if a Call node contains string literal arguments.

        Returns True if any positional or keyword argument is:
        - An ast.Constant with string value
        - An ast.JoinedStr (f-string)
        """
        values = [*call_node.args, *(keyword.value for keyword in call_node.keywords)]
        return any(self._is_string_literal(value) for value in values)

    @staticmethod
    def _is_string_literal(node: ast.expr) -> bool:
        """Check if a node is a string literal or f-string."""
        if isinstance(node, ast.Constant):
            return isinstance(node.value, str)
        return isinstance(node, ast.JoinedStr)
