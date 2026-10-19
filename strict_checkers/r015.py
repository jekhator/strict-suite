"""Checker for R015: Wrap-path separation (P16 - blank-line rhythm in try/except)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity


class R015Checker(BaseChecker):
    """Check wrap-path blank-line rhythm per P16 final calibration.

    Applies ONLY to wrap-function try/except constructs:
    - Nested function inside a wrapper class/method
    - Try/except block with re-raise in except
    - NOT handler if/else constructs

    Checks exactly two things:
    (a) Statement groups within a leg are separated by EXACTLY one blank line
        - Flag 2+ consecutive blanks inside a leg
    (b) The timing-capture pair (perf_counter assignment + round latency line)
        is contiguous - flag any blank inside it
    """

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try statements to check wrap-path blank-line rhythm."""
        if not self.is_suppressed(node, "R015") and self._is_wrap_function_try(node):
            self._check_wrap_function_structure(node)

        self.generic_visit(node)

    @staticmethod
    def _is_wrap_function_try(node: ast.Try) -> bool:
        """Check if try block is within a wrap function (a handler re-raises)."""
        return any(
            isinstance(stmt, ast.Raise)
            for handler in node.handlers
            for stmt in handler.body
        )

    def _check_wrap_function_structure(self, node: ast.Try) -> None:
        """Check per-leg blank-line structure."""
        if node.body:
            self._check_leg_structure(node.body, "try")

        for handler in node.handlers:
            if handler.body:
                self._check_leg_structure(handler.body, "except")

    def _check_leg_structure(self, statements: list[ast.stmt], leg_type: str) -> None:
        """Check per-leg structure: group separation and timing-capture contiguity."""
        self._check_timing_capture_contiguity(statements)
        self._check_group_separation(statements, leg_type)

    def _check_group_separation(self, statements: list[ast.stmt], leg_type: str) -> None:
        """Check that statement groups are separated by EXACTLY one blank line."""
        for curr, next_stmt in zip(statements, statements[1:], strict=False):
            if curr.end_lineno is None or next_stmt.lineno is None:
                continue

            gap = next_stmt.lineno - curr.end_lineno
            # gap == 1: no blank (statements are contiguous)
            # gap == 2: one blank (correct separation)
            # gap > 2: multiple blanks (incorrect)
            if gap > 2:
                self.add_violation(
                    rule_id="R015",
                    severity=RuleSeverity.INFO,
                    line=next_stmt.lineno,
                    col=0,
                    message=f"{leg_type.capitalize()} leg: statement groups must be separated by EXACTLY one blank line.",
                )

    def _check_timing_capture_contiguity(self, statements: list[ast.stmt]) -> None:
        """Check that timing-capture pair (perf_counter + latency calculation) has zero internal blanks."""
        for curr, next_stmt in zip(statements, statements[1:], strict=False):
            if not (self._is_timing_start(curr) and self._is_timing_end(next_stmt)):
                continue
            if curr.end_lineno is None or next_stmt.lineno is None:
                continue

            gap = next_stmt.lineno - curr.end_lineno
            if gap > 1:
                self.add_violation(
                    rule_id="R015",
                    severity=RuleSeverity.INFO,
                    line=next_stmt.lineno,
                    col=0,
                    message="Timing-capture pair (perf_counter + latency calc) must be contiguous (no blank lines within).",
                )

    def _is_timing_start(self, stmt: ast.stmt) -> bool:
        """Check if statement is a timing-start (perf_counter call)."""
        return isinstance(stmt, ast.Assign) and self._contains_perf_counter(stmt.value)

    def _is_timing_end(self, stmt: ast.stmt) -> bool:
        """Check if statement is a timing-end (latency calculation with round)."""
        if not isinstance(stmt, ast.Assign):
            return False
        has_latency_target = any(
            isinstance(target, ast.Name) and "latency" in target.id
            for target in stmt.targets
        )
        return has_latency_target and self._contains_round(stmt.value)

    @staticmethod
    def _contains_perf_counter(node: ast.expr) -> bool:
        """Check whether an expression calls perf_counter, bare or as an attribute."""
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            if isinstance(child.func, ast.Attribute) and child.func.attr == "perf_counter":
                return True
            if isinstance(child.func, ast.Name) and child.func.id == "perf_counter":
                return True
        return False

    @staticmethod
    def _contains_round(node: ast.expr) -> bool:
        """Check whether an expression calls the bare round builtin."""
        return any(
            isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == "round"
            for child in ast.walk(node)
        )
