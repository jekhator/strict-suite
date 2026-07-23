"""Checker for R012: Call fits on one line but is exploded (P3 amendment)."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity, Violation


class R012Checker(BaseChecker):
    """Check for multi-line calls that would fit on a single line within 100 chars.

    Only flags calls with very few arguments (1-2) that span multiple lines
    unnecessarily, avoiding false positives for intentional vertical formatting
    of complex calls.
    """

    def visit_Call(self, node: ast.Call) -> None:
        """Visit call expressions to check fits-one-line-stays rule."""
        if self.is_suppressed(node, "R012"):
            self.generic_visit(node)
            return

        if len(self.lines) == 0 or node.end_lineno is None or node.lineno is None:
            self.generic_visit(node)
            return

        if node.end_lineno <= node.lineno:
            self.generic_visit(node)
            return

        arg_count = len(node.args) + len(node.keywords)
        if arg_count != 1:
            self.generic_visit(node)
            return

        if node.end_lineno - node.lineno < 2:
            self.generic_visit(node)
            return

        try:
            reconstructed = self._reconstruct_call(node, node.lineno, node.end_lineno)
            if reconstructed and len(reconstructed) <= 80:
                self.violations.append(
                    Violation(
                        rule_id="R012",
                        severity=RuleSeverity.INFO,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message="Single-argument call unnecessarily split across lines. Keep on one line.",
                    )
                )
        except Exception:
            pass

        self.generic_visit(node)

    def _reconstruct_call(self, node: ast.Call, start_line: int, end_line: int) -> str | None:
        """Attempt to reconstruct the call as a single line."""
        try:
            relevant_lines = self.lines[start_line - 1 : end_line]
            reconstructed = " ".join(line.strip() for line in relevant_lines)
            reconstructed = self._normalize_spacing(reconstructed)
            return reconstructed
        except Exception:
            return None

    def _normalize_spacing(self, text: str) -> str:
        """Normalize whitespace in reconstructed text."""
        result = []
        in_string = False
        string_char = None
        i = 0

        while i < len(text):
            char = text[i]

            if char in ('"', "'") and (i == 0 or text[i - 1] != "\\"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False

            if in_string:
                result.append(char)
            elif char == " " and result and result[-1] == " ":
                pass
            else:
                result.append(char)

            i += 1

        return "".join(result).strip()
