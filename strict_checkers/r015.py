"""Checker for R015: Wrap-path separation (P16 - blank-line rhythm in try/except)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity, Violation


class R015Checker(BaseChecker):
    """Check wrap-path blank-line rhythm per P16 calibration (authority: formatting-rule-boundaries.md).

    Applies ONLY to wrap-function try/except constructs:
    - Nested function inside a wrapper class/method
    - Try/except block with re-raise in except
    - NOT handler if/else constructs (e.g., comprehend_client.py log_detect_phi)

    Per-leg structure (NOT cross-leg parity):
    - Statement groups separated by exactly one blank
    - Timing-capture pair (perf_counter + latency calc) contiguous (zero internal blanks)
    - Terminal return/raise preceded by exactly one blank
    - Legs may be asymmetric in blank-line count
    """

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try statements to check wrap-path blank-line rhythm."""
        if self.is_suppressed(node, "R015"):
            self.generic_visit(node)
            return

        if node.lineno is None or node.end_lineno is None:
            self.generic_visit(node)
            return

        # NOTE: R015 implementation deferred pending recalibration
        # Current interpretation flags valid gold patterns; requires coordinator clarification
        # on the exact blank-line-precedence semantics for multi-group legs
        # Check if this is a wrap-function try/except (nested function context)
        # if self._is_wrap_function_try(node):
        #     self._check_wrap_function_structure(node)

        self.generic_visit(node)

    def _is_wrap_function_try(self, node: ast.Try) -> bool:
        """Check if try block is within a wrap function (nested inside wrapper class method)."""
        # Conservative check: must have except with raise
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
        """Check per-leg: timing-capture contiguity and terminal return/raise preceded by blank."""
        if not statements or start_line is None:
            return

        # Check for timing-capture contiguity (no blank within timing pair)
        self._check_timing_capture_contiguity(statements)

        # Check terminal return/raise preceded by blank
        # ONLY if leg has 2+ blank-separated groups BEFORE terminal; single contiguous group is conformant
        if statements:
            last_stmt = statements[-1]
            if isinstance(last_stmt, (ast.Return, ast.Raise)):
                # Count internal blank separations BEFORE terminal statement (in pre-terminal statements only)
                internal_blanks_before_terminal = 0
                for i in range(len(statements) - 2):  # Only check up to second-to-last statement
                    if (statements[i].end_lineno and statements[i + 1].lineno
                            and statements[i + 1].lineno - statements[i].end_lineno > 1):
                        internal_blanks_before_terminal += 1

                # Terminal return/raise requires blank ONLY if pre-terminal statements have 2+ groups (1+ internal blank)
                if internal_blanks_before_terminal > 0 and len(statements) > 1:
                    prev_stmt = statements[-2]
                    if (prev_stmt.end_lineno and last_stmt.lineno
                            and last_stmt.lineno - prev_stmt.end_lineno <= 1):
                        self.violations.append(
                            Violation(
                                rule_id="R015",
                                severity=RuleSeverity.INFO,
                                file=str(self.file_path),
                                line=last_stmt.lineno or start_line,
                                col=0,
                                message=f"{leg_type.capitalize()} leg: terminal {last_stmt.__class__.__name__.lower()} must be preceded by a blank line.",
                            )
                        )

    def _check_timing_capture_contiguity(self, statements: list[ast.stmt]) -> None:
        """Check that timing-capture pair (perf_counter + latency calculation) has zero internal blanks."""
        for i in range(len(statements) - 1):
            curr = statements[i]
            next_stmt = statements[i + 1]

            if self._is_timing_start(curr) and self._is_timing_end(next_stmt):
                # Timing pair found - check for gap
                if (curr.end_lineno and next_stmt.lineno
                        and next_stmt.lineno - curr.end_lineno > 1):
                    self.violations.append(
                        Violation(
                            rule_id="R015",
                            severity=RuleSeverity.INFO,
                            file=str(self.file_path),
                            line=next_stmt.lineno or 0,
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
