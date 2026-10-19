"""Checker for R013: Signature grouping (P14 - compact method signatures)."""

import ast
from collections import defaultdict

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity

MAX_PARAMS_PER_LINE = 5
MAX_PARAMS_BEFORE_CHECK = 3


class R013Checker(BaseChecker):
    """Check compact method signatures per P14 calibration.

    Per 2026-07-23 calibration:
    - Handler methods (log_*, record_*, wrap_*): 2-5 params per line
    - Factory classmethods (@classmethod): NEVER flag (any grouping OK)
    - Short signatures (<=3 params): no enforcement
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to check signature grouping."""
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions to check signature grouping."""
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check one function unless it is suppressed or has no end line."""
        if node.end_lineno is None or self.is_suppressed(node, "R013"):
            return
        self._check_signature(node)

    def _check_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check signature formatting per P14 calibration."""
        params_after_self = self._get_params_after_self(node.args)

        if len(params_after_self) <= MAX_PARAMS_BEFORE_CHECK:
            return

        if node.lineno == node.end_lineno:
            return

        if self._is_classmethod(node):
            return

        if not self._is_handler_method(node.name):
            return

        self._check_handler_signature(params_after_self)

    @staticmethod
    def _get_params_after_self(args: ast.arguments) -> list[ast.arg]:
        """Extract regular parameters after self/cls (excluding *args, **kwargs)."""
        return [*args.args[1:], *args.posonlyargs, *args.kwonlyargs]

    @staticmethod
    def _is_classmethod(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if function is a classmethod (never flag)."""
        return any(
            isinstance(decorator, ast.Name) and decorator.id == "classmethod"
            for decorator in node.decorator_list
        )

    @staticmethod
    def _is_handler_method(method_name: str) -> bool:
        """Check if method is a handler (log_*, record_*, wrap_*)."""
        return method_name.startswith(("log_", "record_", "wrap_"))

    def _check_handler_signature(self, params: list[ast.arg]) -> None:
        """Check handler signature for proper grouping (2-5 per line)."""
        param_lines: dict[int, list[str]] = defaultdict(list)
        for param in params:
            param_lines[param.lineno].append(param.arg)

        for line_num, param_names in sorted(param_lines.items()):
            param_count = len(param_names)
            if param_count > MAX_PARAMS_PER_LINE:
                self.add_violation(
                    rule_id="R013",
                    severity=RuleSeverity.INFO,
                    line=line_num,
                    col=0,
                    message=f"Handler signature line has {param_count} params (>5). Group 2-5 per line.",
                )
