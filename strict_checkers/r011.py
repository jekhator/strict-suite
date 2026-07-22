"""Checker for R011: String literal at raise site."""

import ast

from strict_checkers.base import BaseChecker
from strict_inspection import PathClassifier
from strict_rules import RuleSeverity, Violation


class R011Checker(BaseChecker):
    """Check for string literals in raise exception arguments.

    Enforces that exception message arguments must be references to ERR_*
    constants (via const.* or similar), never inline string literals or
    f-strings.
    """

    def visit_Raise(self, node: ast.Raise) -> None:
        """Visit raise statements to find string literal messages."""
        if PathClassifier.is_test_file(self.file_path):
            self.generic_visit(node)
            return

        if self._is_constant_module(self.file_path):
            self.generic_visit(node)
            return

        if node.exc is None:
            self.generic_visit(node)
            return

        if not isinstance(node.exc, ast.Call):
            self.generic_visit(node)
            return

        if self.is_suppressed(node, "R011"):
            self.generic_visit(node)
            return

        has_literal = self._check_for_string_literals(node.exc)
        if has_literal:
            self.violations.append(
                Violation(
                    rule_id="R011",
                    severity=RuleSeverity.HIGH,
                    file=str(self.file_path),
                    line=node.lineno,
                    col=node.col_offset,
                    message="String literal found in raise statement. Extract to constants/<feature>.py as ERR_<DOMAIN>_<CONDITION>, reference via const.",
                )
            )

        self.generic_visit(node)

    def _is_constant_module(self, file_path) -> bool:
        """Check if file is a constants module."""
        return (
            file_path.name == "constants.py"
            or file_path.name.endswith("_const.py")
            or "constants" in str(file_path)
        )

    def _check_for_string_literals(self, call_node: ast.Call) -> bool:
        """Check if a Call node contains string literal arguments.

        Returns True if any positional or keyword argument is:
        - An ast.Constant with string value
        - An ast.JoinedStr (f-string)
        """
        for arg in call_node.args:
            if self._is_string_literal(arg):
                return True

        for keyword in call_node.keywords:
            if self._is_string_literal(keyword.value):
                return True

        return False

    def _is_string_literal(self, node: ast.expr) -> bool:
        """Check if a node is a string literal or f-string."""
        if isinstance(node, ast.Constant):
            return isinstance(node.value, str)
        if isinstance(node, ast.JoinedStr):
            return True
        return False
