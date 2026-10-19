"""Checker for R009: Module-level functions without a recorded reason."""

import ast

from strict_checkers.base import BaseChecker
from strict_inspection import PathClassifier
from strict_rules import RuleSeverity


class R009Checker(BaseChecker):
    """Advise on module-level functions that have no recorded reason.

    A method on a class is the default shape. A module-level function is exempt
    when it is an entry point, a decorated framework registration point, a
    protocol-required module hook, or carries an exception tag on the def line
    or in the first line of its docstring.
    """

    ALLOWED_ENTRY_POINTS = {"main", "handle_command", "handle_event", "handle_request"}

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module to find top-level function definitions."""
        if PathClassifier.is_test_file(self.file_path):
            return

        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue

            if self._is_exempt(item):
                continue

            if self.is_suppressed(item, "R009"):
                continue

            self.add_violation(
rule_id="R009", severity=RuleSeverity.INFO, line=item.lineno, col=item.col_offset,
message=(
                        f"Module-level function '{item.name}': a method on a class is the "
                        "default shape. Keep it module-level only when that is the optimal "
                        "shape (framework hook, entry point, stateless helper with no owning "
                        "class) and record why with '# module-level: <reason>' on the def "
                        "line. Entry points need no tag: main, handle_*."
                    ),
)

        self.generic_visit(node)

    def _is_exempt(self, node: ast.FunctionDef) -> bool:
        """Check whether a module-level function is exempt from R009."""
        if node.decorator_list:
            return True
        if self._is_entry_point(node.name) or self._is_protocol_hook(node.name):
            return True
        return self.has_exception_tag(node)

    def _is_entry_point(self, name: str) -> bool:
        """Check if function name is an allowed entry point."""
        return name in self.ALLOWED_ENTRY_POINTS or name.startswith("handle_")

    def _is_protocol_hook(self, name: str) -> bool:
        """Check if function is a dunder module hook or a pytest hook."""
        is_dunder = name.startswith("__") and name.endswith("__")
        return is_dunder or name.startswith("pytest_")
