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

        if node.lineno is None or node.end_lineno is None:
            self.generic_visit(node)
            return

        if len(node.keywords) != 2:
            self.generic_visit(node)
            return

        if node.lineno == node.end_lineno:
            self.generic_visit(node)
            return

        kwarg_lines = {}
        for keyword in node.keywords:
            if keyword.lineno not in kwarg_lines:
                kwarg_lines[keyword.lineno] = []
            kwarg_name = keyword.arg if keyword.arg else "**"
            kwarg_lines[keyword.lineno].append(kwarg_name)

        sorted_lines = sorted(kwarg_lines.items())

        if len(sorted_lines) == 0:
            self.generic_visit(node)
            return

        one_per_line_count = sum(1 for _, names in sorted_lines if len(names) == 1)

        if one_per_line_count == len(sorted_lines):
            self.violations.append(
                Violation(
                    rule_id="R014",
                    severity=RuleSeverity.INFO,
                    file=str(self.file_path),
                    line=node.lineno,
                    col=0,
                    message="Call has 2 kwargs, each on separate line. Group on one line.",
                )
            )

        self.generic_visit(node)
