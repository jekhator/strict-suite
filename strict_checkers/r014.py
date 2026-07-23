"""Checker for R014: Kwarg-call grouping (P15 - packed keyword groups)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity, Violation


class R014Checker(BaseChecker):
    """Check packed keyword groups per P15 calibration (authority: formatting-rule-boundaries.md).

    Conditions:
    1. Log-event calls (first arg = LOG_EVENT_* constant reference):
       - >=4 kwargs: pack 2-3 per line (first line may carry constant)
       - 2-3 kwargs: FULL-EXPLODE one-per-line (constant on its own line)
    2. DTO/Model construction (complex semantic DTOs): one-field-per-line never flagged
    3. Simple value objects (*Event, *Record, *Result, *Metrics): may pack per P3 (not flagged)

    Note: Gold-29 baseline (sha 925f7027) pre-dates full-explode rule for 2-3 kwargs;
    those packed calls are grandfathered. Current branch applies full-explode rule.
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
        """Check kwarg grouping per P15."""
        kwarg_count = len(node.keywords)
        if kwarg_count < 2:
            return

        is_log_event = self._is_log_event_call(node)

        if is_log_event:
            self._check_log_event_kwargs(node, kwarg_count)

    def _is_log_event_call(self, node: ast.Call) -> bool:
        """Check if call is a log-event call with LOG_EVENT_* constant as first positional arg."""
        if not node.args:
            return False

        if not isinstance(node.func, ast.Attribute):
            return False

        # Must be self.log_* or cls.log_* pattern
        if not node.func.attr.startswith("log"):
            return False

        # Check if first positional arg is a LOG_EVENT_* constant reference
        first_arg = node.args[0]
        return self._is_log_event_constant(first_arg)

    def _is_log_event_constant(self, node: ast.expr) -> bool:
        """Check if node is a LOG_EVENT_* constant reference (e.g., const.LOG_EVENT_*)."""
        if isinstance(node, ast.Attribute):
            return "LOG_EVENT" in node.attr
        if isinstance(node, ast.Name):
            return "LOG_EVENT" in node.id
        return False

    def _check_log_event_kwargs(self, node: ast.Call, kwarg_count: int) -> None:
        """Check log-event call kwarg grouping per P15 spec."""
        kwarg_lines: dict[int, list[str]] = {}
        for keyword in node.keywords:
            line = keyword.lineno  # type: ignore[union-attr]
            if line not in kwarg_lines:
                kwarg_lines[line] = []
            kwarg_lines[line].append(keyword.arg or "**kwarg")

        sorted_lines = sorted(kwarg_lines.items())
        first_kwarg_line = sorted_lines[0][0] if sorted_lines else None

        if kwarg_count >= 4:
            self._check_log_event_pack_2_3(sorted_lines, first_kwarg_line, node.lineno)
        elif kwarg_count in (2, 3):
            self._check_log_event_full_explode(sorted_lines, node)

    def _check_log_event_pack_2_3(
        self, sorted_lines: list[tuple[int, list[str]]], first_kwarg_line: int | None, call_line: int | None
    ) -> None:
        """Check >=4 kwargs: must pack 2-3 per line (first line may carry constant)."""
        for line_idx, (line_num, kwarg_names) in enumerate(sorted_lines):
            count = len(kwarg_names)
            is_first_line = line_num == first_kwarg_line and call_line is not None and line_num - call_line < 2

            # First line: may have 1-2 kwargs (if it carries the constant)
            # Subsequent lines: must have 2-3 kwargs
            if is_first_line:
                if count > 2:
                    self.violations.append(
                        Violation(
                            rule_id="R014",
                            severity=RuleSeverity.INFO,
                            file=str(self.file_path),
                            line=line_num,
                            col=0,
                            message=f"Log event call >=4 kwargs: first line may have 1-2 kwargs (found {count}).",
                        )
                    )
            else:
                if count == 1 or count > 3:
                    self.violations.append(
                        Violation(
                            rule_id="R014",
                            severity=RuleSeverity.INFO,
                            file=str(self.file_path),
                            line=line_num,
                            col=0,
                            message=f"Log event call >=4 kwargs: pack 2-3 per line (found {count}).",
                        )
                    )

    def _check_log_event_full_explode(
        self, sorted_lines: list[tuple[int, list[str]]], node: ast.Call
    ) -> None:
        """Check 2-3 kwargs: must FULL-EXPLODE one-per-line (constant on its own line)."""
        # For 2-3 kwarg calls, each kwarg should be on its own line
        # Event constant should be on its own line (no kwargs on that line)
        for line_num, kwarg_names in sorted_lines:
            if len(kwarg_names) != 1:
                self.violations.append(
                    Violation(
                        rule_id="R014",
                        severity=RuleSeverity.INFO,
                        file=str(self.file_path),
                        line=line_num,
                        col=0,
                        message="Log event call 2-3 kwargs: FULL-EXPLODE one-per-line.",
                    )
                )
