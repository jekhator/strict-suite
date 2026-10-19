"""Checker for R007: Pytest fixtures defined outside conftest.py."""

import ast

from strict_checkers.base import BaseChecker
from strict_inspection import PathClassifier
from strict_rules import RuleSeverity


class R007Checker(BaseChecker):
    """Check for pytest fixtures defined outside conftest.py."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to find pytest fixtures."""
        is_fixture = any(
            self.is_pytest_fixture_decorator(decorator)
            for decorator in node.decorator_list
        )
        if (
            is_fixture
            and PathClassifier.is_test_file(self.file_path)
            and self.file_path.name != "conftest.py"
            and not self.is_suppressed(node, "R007")
        ):
            self.add_violation(
                rule_id="R007",
                severity=RuleSeverity.MEDIUM,
                line=node.lineno,
                col=node.col_offset,
                message=f"Pytest fixture defined outside conftest.py: {node.name}. Move to conftest.py.",
            )

        self.generic_visit(node)
