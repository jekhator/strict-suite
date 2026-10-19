"""Checker for R014: Kwarg-call grouping (P15 - packed keyword groups)."""

import ast
from collections import defaultdict

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity

MAX_KWARGS_PER_LINE = 3


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
        if (
            node.keywords
            and node.end_lineno is not None
            and node.lineno != node.end_lineno
            and not self.is_suppressed(node, "R014")
        ):
            self._check_call_kwargs(node)

        self.generic_visit(node)

    def _check_call_kwargs(self, node: ast.Call) -> None:
        """Check kwarg grouping per P15."""
        kwarg_count = len(node.keywords)
        if kwarg_count < 2:
            return

        if self._is_log_event_call(node):
            self._check_log_event_kwargs(node, kwarg_count)

    def _is_log_event_call(self, node: ast.Call) -> bool:
        """Check if call is a log-event call with LOG_EVENT_* constant as first positional arg."""
        if not node.args or not isinstance(node.func, ast.Attribute):
            return False

        # Must be self.log_* or cls.log_* pattern
        if not node.func.attr.startswith("log"):
            return False

        return self._is_log_event_constant(node.args[0])

    @staticmethod
    def _is_log_event_constant(node: ast.expr) -> bool:
        """Check if node is a LOG_EVENT_* constant reference (e.g., const.LOG_EVENT_*)."""
        if isinstance(node, ast.Attribute):
            return "LOG_EVENT" in node.attr
        if isinstance(node, ast.Name):
            return "LOG_EVENT" in node.id
        return False

    def _check_log_event_kwargs(self, node: ast.Call, kwarg_count: int) -> None:
        """Check log-event call kwarg grouping per P15 spec."""
        kwarg_lines: dict[int, list[str]] = defaultdict(list)
        for keyword in node.keywords:
            kwarg_lines[keyword.lineno].append(keyword.arg or "**kwarg")

        sorted_lines = sorted(kwarg_lines.items())

        if kwarg_count >= 4:
            self._check_log_event_pack_2_3(sorted_lines)
        elif kwarg_count in (2, 3):
            self._check_log_event_full_explode(sorted_lines)

    def _check_log_event_pack_2_3(self, sorted_lines: list[tuple[int, list[str]]]) -> None:
        """Check >=4 kwargs: flag ONLY over-packing (>3 per line). One-per-line is never flagged."""
        for line_num, kwarg_names in sorted_lines:
            count = len(kwarg_names)
            if count > MAX_KWARGS_PER_LINE:
                self.add_violation(
                    rule_id="R014",
                    severity=RuleSeverity.INFO,
                    line=line_num,
                    col=0,
                    message=f"Log event call: pack maximum 3 kwargs per line (found {count}).",
                )

    def _check_log_event_full_explode(self, sorted_lines: list[tuple[int, list[str]]]) -> None:
        """Check 2-3 kwargs: must FULL-EXPLODE one-per-line (constant on its own line)."""
        for line_num, kwarg_names in sorted_lines:
            if len(kwarg_names) != 1:
                self.add_violation(
                    rule_id="R014",
                    severity=RuleSeverity.INFO,
                    line=line_num,
                    col=0,
                    message="Log event call 2-3 kwargs: FULL-EXPLODE one-per-line.",
                )
