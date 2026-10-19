"""Checker for R012: Call fits on one line but is exploded (P3 amendment)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity

MAX_COLLAPSED_LENGTH = 80


class R012Checker(BaseChecker):
    """Check for multi-line calls that would fit on a single line within 100 chars.

    Only flags calls with very few arguments (1-2) that span multiple lines
    unnecessarily, avoiding false positives for intentional vertical formatting
    of complex calls.
    """

    def visit_Call(self, node: ast.Call) -> None:
        """Visit call expressions to check fits-one-line-stays rule."""
        if self._is_collapsible(node):
            self.add_violation(
                rule_id="R012",
                severity=RuleSeverity.INFO,
                line=node.lineno,
                col=node.col_offset,
                message="Single-argument call unnecessarily split across lines. Keep on one line.",
            )

        self.generic_visit(node)

    def _is_collapsible(self, node: ast.Call) -> bool:
        """Check whether a single-argument call spans lines but reconstructs within the length limit."""
        if self.is_suppressed(node, "R012") or node.end_lineno is None:
            return False

        if node.end_lineno - node.lineno < 2:
            return False

        if len(node.args) + len(node.keywords) != 1:
            return False

        reconstructed = self._normalize_spacing(
            " ".join(line.strip() for line in self.lines[node.lineno - 1 : node.end_lineno])
        )
        return bool(reconstructed) and len(reconstructed) <= MAX_COLLAPSED_LENGTH

    @staticmethod
    def _normalize_spacing(text: str) -> str:
        """Collapse runs of spaces outside string literals and strip the ends."""
        result: list[str] = []
        string_char: str | None = None

        for index, char in enumerate(text):
            escaped = index > 0 and text[index - 1] == "\\"
            if char in ('"', "'") and not escaped:
                if string_char is None:
                    string_char = char
                elif char == string_char:
                    string_char = None

            in_string = string_char is not None
            if in_string or char != " " or not (result and result[-1] == " "):
                result.append(char)

        return "".join(result).strip()
