"""Checker for R005: Validator not using DTO.from_dict() pattern."""

import ast

from strict_module.checkers.base import BaseChecker
from strict_module.rules import RuleSeverity, Violation


class R005Checker(BaseChecker):
    """Check for validators using DTO.from_dict() pattern."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        if not node.name.startswith("validate_"):
            self.generic_visit(node)
            return

        if self.is_suppressed(node, "R005"):
            self.generic_visit(node)
            return

        has_payload_param = any(
            arg.arg == "payload" for arg in node.args.args + node.args.kwonlyargs
        )

        if not has_payload_param:
            self.generic_visit(node)
            return

        has_from_dict = self._has_from_dict_call(node)
        has_validation_error = self._has_validation_error(node)

        if not (has_from_dict or has_validation_error):
            self.violations.append(
                Violation(
                    rule_id="R005",
                    severity=RuleSeverity.LOW,
                    file=str(self.file_path),
                    line=node.lineno,
                    col=node.col_offset,
                    message=f"Validator does not use DTO.from_dict() pattern: {node.name}",
                )
            )

        self.generic_visit(node)

    def _has_from_dict_call(self, node: ast.FunctionDef) -> bool:
        """Check if function body calls .from_dict()."""
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                if isinstance(item.func, ast.Attribute):
                    if item.func.attr == "from_dict":
                        return True
        return False

    def _has_validation_error(self, node: ast.FunctionDef) -> bool:
        """Check if function raises ValidationError."""
        for item in ast.walk(node):
            if isinstance(item, ast.Raise):
                if isinstance(item.exc, ast.Call):
                    if isinstance(item.exc.func, ast.Name):
                        if "ValidationError" in item.exc.func.id:
                            return True
        return False
