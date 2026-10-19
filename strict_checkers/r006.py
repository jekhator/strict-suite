"""Checker for R006: typing.Any in signature."""

import ast
from collections.abc import Iterator

from strict_checkers.base import BaseChecker
from strict_inspection import AnnotationInspector, PathClassifier
from strict_rules import RuleSeverity


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

        for label, annotation in self._parameter_annotations(node):
            if annotation is not None and AnnotationInspector.contains_any(annotation):
                self._report(node, f"typing.Any in {label}: {node.name}")
                return

        if node.returns is not None and AnnotationInspector.contains_any(node.returns):
            self._report(node, f"typing.Any in return type: {node.name}")

        self.generic_visit(node)

    @staticmethod
    def _parameter_annotations(
        node: ast.FunctionDef,
    ) -> Iterator[tuple[str, ast.expr | None]]:
        """Yield each parameter label with its annotation, including *args and **kwargs."""
        for arg in (*node.args.args, *node.args.posonlyargs, *node.args.kwonlyargs):
            yield "parameter", arg.annotation
        if node.args.vararg is not None:
            yield "*args", node.args.vararg.annotation
        if node.args.kwarg is not None:
            yield "**kwargs", node.args.kwarg.annotation

    def _report(self, node: ast.FunctionDef, message: str) -> None:
        """Append an R006 HIGH violation for a function."""
        self.add_violation(
            rule_id="R006",
            severity=RuleSeverity.HIGH,
            line=node.lineno,
            col=node.col_offset,
            message=message,
        )
