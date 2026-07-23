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
        args = node.args

        params_after_self = []
        if len(args.args) > 0:
            params_after_self = args.args[1:]
        params_after_self += args.posonlyargs + args.kwonlyargs
        if args.vararg:
            params_after_self.append(args.vararg)
        if args.kwarg:
            params_after_self.append(args.kwarg)

        if len(params_after_self) < 3 or len(params_after_self) > 4:
            return

        if node.lineno == node.end_lineno:
            return

        param_lines = {}
        for param in params_after_self:
            if param.lineno not in param_lines:
                param_lines[param.lineno] = []
            param_lines[param.lineno].append(param.arg)

        sorted_lines = sorted(param_lines.items())

        if len(sorted_lines) == 0:
            return

        one_per_line_count = sum(1 for _, names in sorted_lines if len(names) == 1)

        if one_per_line_count == len(sorted_lines):
            self.violations.append(
                Violation(
                    rule_id="R013",
                    severity=RuleSeverity.INFO,
                    file=str(self.file_path),
                    line=node.lineno,
                    col=0,
                    message=f"Signature has {len(params_after_self)} parameters, each on separate line. Group 2-3 per line.",
                )
            )
