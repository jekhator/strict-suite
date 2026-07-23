"""Checker for R015: Wrap-path separation (P16 - blank-line rhythm in try/except)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity, Violation


class R015Checker(BaseChecker):
    """Check for wrap-path blank-line rhythm: try and except legs mirror each other.

    The canonical rule from P16 is complex and applies to wrapped operations.
    This simplified checker currently does NOT flag violations, as the rule
    requires understanding operation intent (setup/execution/capture/return)
    which is difficult to infer from AST alone.

    Future work: expand to detect clearly asymmetric blank-line patterns
    in wrap function pairs (after collecting concrete test cases).
    """

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try statements to check blank-line rhythm."""
        if self.is_suppressed(node, "R015"):
            self.generic_visit(node)
            return

        if not node.handlers:
            self.generic_visit(node)
            return

        try_stmt_count = len(node.body)

        for handler in node.handlers:
            if self.is_suppressed(handler, "R015"):
                continue

            handler_stmt_count = len(handler.body)

            difference = abs(try_stmt_count - handler_stmt_count)

            if difference > 3:
                self.violations.append(
                    Violation(
                        rule_id="R015",
                        severity=RuleSeverity.INFO,
                        file=str(self.file_path),
                        line=handler.lineno,
                        col=0,
                        message=f"Except block has {handler_stmt_count} statements vs try's {try_stmt_count}. Mirror try's internal structure.",
                    )
                )

        self.generic_visit(node)
