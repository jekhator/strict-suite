"""Checker for R008: Bare module-level test function."""

import ast

from strict_checkers.base import BaseChecker
from strict_inspection import PathClassifier
from strict_rules import RuleSeverity


class R008Checker(BaseChecker):
    """Check for bare module-level test functions."""

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module to find top-level test functions."""
        if not PathClassifier.is_test_file(self.file_path):
            return

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith("test_"):
                    if self.is_suppressed(item, "R008"):
                        continue

                    self.add_violation(
rule_id="R008", severity=RuleSeverity.MEDIUM, line=item.lineno, col=item.col_offset,
message=f"Module-level test function: {item.name}. Move into Test<Concern> class.",
)
