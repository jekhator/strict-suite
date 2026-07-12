"""Checker for R006: typing.Any in signature."""

import ast

from strict_module.checkers.base import BaseChecker
from strict_module.inspection import AnnotationInspector, PathClassifier
from strict_module.rules import RuleSeverity, Violation


class R006Checker(BaseChecker):
    """Check for typing.Any in service-layer function signatures."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        if not PathClassifier.is_service_path(self.file_path, self.config.r006_paths):
            self.generic_visit(node)
            return

        if self.is_suppressed(node, "R006"):
            self.generic_visit(node)
            return

        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation and AnnotationInspector.contains_any(arg.annotation):
                self.violations.append(
                    Violation(
                        rule_id="R006",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"typing.Any in parameter: {node.name}",
                    )
                )
                return

        if node.args.vararg and node.args.vararg.annotation:
            if AnnotationInspector.contains_any(node.args.vararg.annotation):
                self.violations.append(
                    Violation(
                        rule_id="R006",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"typing.Any in *args: {node.name}",
                    )
                )
                return

        if node.args.kwarg and node.args.kwarg.annotation:
            if AnnotationInspector.contains_any(node.args.kwarg.annotation):
                self.violations.append(
                    Violation(
                        rule_id="R006",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"typing.Any in **kwargs: {node.name}",
                    )
                )
                return

        if node.returns and AnnotationInspector.contains_any(node.returns):
            self.violations.append(
                Violation(
                    rule_id="R006",
                    severity=RuleSeverity.HIGH,
                    file=str(self.file_path),
                    line=node.lineno,
                    col=node.col_offset,
                    message=f"typing.Any in return type: {node.name}",
                )
            )

        self.generic_visit(node)
