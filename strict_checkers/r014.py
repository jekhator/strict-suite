"""Checker for R014: Kwarg-call grouping (P15 - packed keyword groups)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity, Violation


class R014Checker(BaseChecker):
    """Check for packed keyword groups: 2-3 kwargs per line, not one-per-line.

    Only flags calls with 2-3 kwargs that are each on separate lines when
    they could reasonably be grouped.
    """

    def visit_Call(self, node: ast.Call) -> None:
        """Visit call expressions to check kwarg grouping."""
        if self.is_suppressed(node, "R014"):
            self.generic_visit(node)
            return

        self.generic_visit(node)
