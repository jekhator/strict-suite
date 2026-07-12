"""Checker for R007: Pytest fixtures defined outside conftest.py."""

import ast

from strict_module.checkers.base import BaseChecker
from strict_module.inspection import PathClassifier
from strict_module.rules import RuleSeverity, Violation


class R007Checker(BaseChecker):
    """Check for pytest fixtures defined outside conftest.py."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to find pytest fixtures."""
        if not PathClassifier.is_test_file(self.file_path):
            self.generic_visit(node)
            return

        if self.file_path.name == "conftest.py":
            self.generic_visit(node)
            return

        for decorator in node.decorator_list:
            if self._is_pytest_fixture_decorator(decorator):
                if self.is_suppressed(node, "R007"):
                    continue

                self.violations.append(
                    Violation(
                        rule_id="R007",
                        severity=RuleSeverity.MEDIUM,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Pytest fixture defined outside conftest.py: {node.name}. Move to conftest.py.",
                    )
                )

        self.generic_visit(node)

    def _is_pytest_fixture_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is @pytest.fixture."""
        if isinstance(decorator, ast.Name):
            return decorator.id == "fixture"
        elif isinstance(decorator, ast.Attribute):
            if decorator.attr == "fixture":
                if isinstance(decorator.value, ast.Name):
                    if decorator.value.id == "pytest":
                        return True
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id == "fixture"
            elif isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr == "fixture":
                    if isinstance(decorator.func.value, ast.Name):
                        if decorator.func.value.id == "pytest":
                            return True
        return False
