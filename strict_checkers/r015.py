"""Checker for R015: Wrap-path separation (P16 - blank-line rhythm in try/except)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity, Violation


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
        if self.is_suppressed(node, "R015"):
            self.generic_visit(node)
            return

        if node.lineno is None or node.end_lineno is None:
            self.generic_visit(node)
            return

        if self._is_wrap_function_try(node):
            self._check_wrap_function_structure(node)

        self.generic_visit(node)

    def _is_wrap_function_try(self, node: ast.Try) -> bool:
        """Check if try block is within a wrap function (nested inside wrapper class method)."""
        if not node.handlers:
            return False

        for handler in node.handlers:
            for stmt in handler.body:
                if isinstance(stmt, ast.Raise):
                    return True

        return False

    def _check_wrap_function_structure(self, node: ast.Try) -> None:
        """Check per-leg blank-line structure."""
        if node.body:
            self._check_leg_structure(node.body, node.lineno, "try")

        for handler in node.handlers:
            if handler.body:
                self._check_leg_structure(handler.body, handler.lineno, "except")

    def _check_leg_structure(
        self, statements: list[ast.stmt], start_line: int | None, leg_type: str
    ) -> None:
        """Check per-leg structure: group separation and timing-capture contiguity."""
        if not statements or start_line is None:
            return

        # Check for timing-capture contiguity (no blank within timing pair)
        self._check_timing_capture_contiguity(statements)

        # Check for statement group separation: exactly one blank between groups
        self._check_group_separation(statements, leg_type)

    def _check_group_separation(
        self, statements: list[ast.stmt], leg_type: str
    ) -> None:
        """Check that statement groups are separated by EXACTLY one blank line."""
        for i in range(len(statements) - 1):
            curr = statements[i]
            next_stmt = statements[i + 1]

            if curr.end_lineno is None or next_stmt.lineno is None:
                continue

            gap = next_stmt.lineno - curr.end_lineno
            # gap == 1: no blank (statements are contiguous)
            # gap == 2: one blank (correct separation)
            # gap > 2: multiple blanks (incorrect)
            if gap > 2:
                self.violations.append(
                    Violation(
                        rule_id="R015",
                        severity=RuleSeverity.INFO,
                        file=str(self.file_path),
                        line=next_stmt.lineno,
                        col=0,
                        message=f"{leg_type.capitalize()} leg: statement groups must be separated by EXACTLY one blank line.",
                    )
                )

    def _check_timing_capture_contiguity(self, statements: list[ast.stmt]) -> None:
        """Check that timing-capture pair (perf_counter + latency calculation) has zero internal blanks."""
        for i in range(len(statements) - 1):
            curr = statements[i]
            next_stmt = statements[i + 1]

            if self._is_timing_start(curr) and self._is_timing_end(next_stmt):
                # Timing pair found - check for gap
                if curr.end_lineno is not None and next_stmt.lineno is not None:
                    gap = next_stmt.lineno - curr.end_lineno
                    if gap > 1:
                        self.violations.append(
                            Violation(
                                rule_id="R015",
                                severity=RuleSeverity.INFO,
                                file=str(self.file_path),
                                line=next_stmt.lineno,
                                col=0,
                                message="Timing-capture pair (perf_counter + latency calc) must be contiguous (no blank lines within).",
                            )
                        )

    def _is_timing_start(self, stmt: ast.stmt) -> bool:
        """Check if statement is a timing-start (perf_counter call)."""
        if not isinstance(stmt, ast.Assign):
            return False
        return self._contains_perf_counter(stmt.value)

    def _is_timing_end(self, stmt: ast.stmt) -> bool:
        """Check if statement is a timing-end (latency calculation)."""
        if not isinstance(stmt, ast.Assign):
            return False
        # Check for latency_ms = ... with round() call
        for target in stmt.targets:
            if isinstance(target, ast.Name) and "latency" in target.id:
                return self._contains_round(stmt.value)
        return False

    def _contains_perf_counter(self, node: ast.expr) -> bool:
        """Check if node contains perf_counter call."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr == "perf_counter":
                        return True
                elif isinstance(child.func, ast.Name):
                    if child.func.id == "perf_counter":
                        return True
        return False

    def _contains_round(self, node: ast.expr) -> bool:
        """Check if node contains round call."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id == "round":
                        return True
        return False
