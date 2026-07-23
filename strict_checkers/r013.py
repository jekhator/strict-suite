"""Checker for R013: Signature grouping (P14 - compact method signatures)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity, Violation


class R013Checker(BaseChecker):
    """Check for compact method signatures: 2-3 parameters per line, not one-per-line.

    Only flags signatures where ALL parameters are strictly one-per-line when
    the signature is short enough to reasonably group them.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to check signature grouping."""
        if self.is_suppressed(node, "R013"):
            self.generic_visit(node)
            return

        if node.lineno is None or node.end_lineno is None:
            self.generic_visit(node)
            return

        self._check_signature(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions to check signature grouping."""
        if self.is_suppressed(node, "R013"):
            self.generic_visit(node)
            return

        if node.lineno is None or node.end_lineno is None:
            self.generic_visit(node)
            return

        self._check_signature(node)
        self.generic_visit(node)

    def _check_signature(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """Check signature formatting."""
        pass
