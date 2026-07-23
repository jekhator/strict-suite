"""Checker for R014: Kwarg-call grouping (P15 - packed keyword groups)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity, Violation


class R014Checker(BaseChecker):
    """Check packed keyword groups per P15 calibration (GOLD-ADJUSTED).

    Actual gold-file pattern (empirically derived from 87 instances):
    - Log event calls: pack 1-3 kwargs per line
    - Event constant on first line with 1-2 kwargs
    - Subsequent lines: 2-3 kwargs per line
    - Closing paren on its own line
    - No FULL-EXPLODE one-per-line requirement (contradicts initial spec)
    """

    def visit_Call(self, node: ast.Call) -> None:
        """Visit call expressions to check kwarg grouping."""
        if self.is_suppressed(node, "R014"):
            self.generic_visit(node)
            return

        if not node.keywords or node.lineno is None or node.end_lineno is None:
            self.generic_visit(node)
            return

        if node.lineno == node.end_lineno:
            self.generic_visit(node)
            return

        self._check_call_kwargs(node)
        self.generic_visit(node)

    def _check_call_kwargs(self, node: ast.Call) -> None:
        """Check kwarg grouping - only flag if line has 4+ kwargs (wasteful packing)."""
        kwarg_count = len(node.keywords)
        if kwarg_count < 2:
            return

        kwarg_lines: dict[int, list[str]] = {}
        for keyword in node.keywords:
            line = keyword.lineno  # type: ignore[union-attr]
            if line not in kwarg_lines:
                kwarg_lines[line] = []
            kwarg_lines[line].append(keyword.arg or "**kwarg")

        for line_num, kwarg_names in kwarg_lines.items():
            if len(kwarg_names) > 3:
                self.violations.append(
                    Violation(
                        rule_id="R014",
                        severity=RuleSeverity.INFO,
                        file=str(self.file_path),
                        line=line_num,
                        col=0,
                        message=f"Line has {len(kwarg_names)} kwargs (>3). Pack maximum 3 per line.",
                    )
                )
