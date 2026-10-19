"""Checker for R001: Dict[str, Any] or bare collections in signatures."""

import ast

from strict_checkers.base import BaseChecker
from strict_inspection import AnnotationInspector, PathClassifier
from strict_rules import RuleSeverity


class R001Checker(BaseChecker):
    """Check for Dict[str, Any] or bare collections in service-layer function signatures."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        if not PathClassifier.is_service_path(
            self.file_path, self.config.service_paths
        ):
            return

        if self.is_suppressed(node, "R001"):
            return

        parameter_annotations = [
            arg.annotation
            for arg in (*node.args.args, *node.args.posonlyargs, *node.args.kwonlyargs)
        ]
        for special in (node.args.vararg, node.args.kwarg):
            if special is not None:
                parameter_annotations.append(special.annotation)

        for annotation in parameter_annotations:
            if annotation is None:
                continue
            message = self._problem_message(annotation, node.name)
            if message is not None:
                self._report(node, message)
                return

        if node.returns is not None:
            message = self._problem_message(node.returns, node.name)
            if message is not None:
                self._report(node, message)

        self.generic_visit(node)

    def _problem_message(self, annotation: ast.expr, name: str) -> str | None:
        """Return the violation message for an annotation, or None when it is allowed."""
        if AnnotationInspector.is_dict_str_any(annotation):
            return f"Dict[str, Any] in signature: {name}"
        if self.config.strict_collections and AnnotationInspector.is_bare_collection(
            annotation
        ):
            return f"Bare collection type in signature: {name} (use strict_collections=False to disable)"
        return None

    def _report(self, node: ast.FunctionDef, message: str) -> None:
        """Append an R001 HIGH violation for a function."""
        self.add_violation(
rule_id="R001", severity=RuleSeverity.HIGH, line=node.lineno, col=node.col_offset,
message=message,
)
