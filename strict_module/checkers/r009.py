"""Checker for R009: Module-level functions outside allowed entry points."""

import ast

from strict_module.checkers.base import BaseChecker
from strict_module.inspection import PathClassifier
from strict_module.rules import RuleSeverity, Violation


class R009Checker(BaseChecker):
    """Check for bare module-level functions outside allowed entry points."""

    ALLOWED_ENTRY_POINTS = {"main", "handle_command", "handle_event", "handle_request"}

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module to find top-level function definitions."""
        if PathClassifier.is_test_file(self.file_path):
            return

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if self._is_fixture(item):
                    continue

                if self._is_allowed_entry_point(item.name):
                    continue

                if self._has_exception_tag(item):
                    continue

                if self.is_suppressed(item, "R009"):
                    continue

                self.violations.append(
                    Violation(
                        rule_id="R009",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=item.lineno,
                        col=item.col_offset,
                        message=f"Module-level function '{item.name}' found in service path. Every method must be in a class. Allowed exceptions: {self._format_allowed_list()}.",
                    )
                )

        self.generic_visit(node)

    def _is_fixture(self, node: ast.FunctionDef) -> bool:
        """Check if function is a pytest fixture."""
        for decorator in node.decorator_list:
            if self._is_pytest_fixture_decorator(decorator):
                return True
        return False

    def _is_pytest_fixture_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is @pytest.fixture."""
        if isinstance(decorator, ast.Name):
            return decorator.id == "fixture"
        elif isinstance(decorator, ast.Attribute):
            if decorator.attr == "fixture":
                if isinstance(decorator.value, ast.Name):
                    return decorator.value.id == "pytest"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id == "fixture"
            elif isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr == "fixture":
                    if isinstance(decorator.func.value, ast.Name):
                        return decorator.func.value.id == "pytest"
        return False

    def _is_allowed_entry_point(self, name: str) -> bool:
        """Check if function name is an allowed entry point."""
        if name in self.ALLOWED_ENTRY_POINTS:
            return True
        if name.startswith("handle_"):
            return True
        return False

    def _has_exception_tag(self, node: ast.FunctionDef) -> bool:
        """Check if function has an exception tag on the same line."""
        comment_text = self.get_comment_text(node.lineno)
        if not comment_text:
            return False

        for tag in self.config.exception_tags:
            if tag.lower() in comment_text.lower():
                return True

        return False

    def _format_allowed_list(self) -> str:
        """Format allowed entry point names for error message."""
        return ", ".join(sorted(self.ALLOWED_ENTRY_POINTS | {"handle_*"}))
