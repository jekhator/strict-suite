"""Checker for R001: Dict[str, Any] or bare collections in signatures."""

import ast

from strict_checkers.base import BaseChecker
from strict_inspection import AnnotationInspector, PathClassifier
from strict_rules import RuleSeverity, Violation


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

        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation:
                if AnnotationInspector.is_dict_str_any(arg.annotation):
                    self.violations.append(
                        Violation(
                            rule_id="R001",
                            severity=RuleSeverity.HIGH,
                            file=str(self.file_path),
                            line=node.lineno,
                            col=node.col_offset,
                            message=f"Dict[str, Any] in signature: {node.name}",
                        )
                    )
                    return
                elif (
                    self.config.strict_collections
                    and AnnotationInspector.is_bare_collection(arg.annotation)
                ):
                    self.violations.append(
                        Violation(
                            rule_id="R001",
                            severity=RuleSeverity.HIGH,
                            file=str(self.file_path),
                            line=node.lineno,
                            col=node.col_offset,
                            message=f"Bare collection type in signature: {node.name} (use strict_collections=False to disable)",
                        )
                    )
                    return

        if node.args.vararg and node.args.vararg.annotation:
            if AnnotationInspector.is_dict_str_any(node.args.vararg.annotation):
                self.violations.append(
                    Violation(
                        rule_id="R001",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Dict[str, Any] in signature: {node.name}",
                    )
                )
                return
            elif (
                self.config.strict_collections
                and AnnotationInspector.is_bare_collection(node.args.vararg.annotation)
            ):
                self.violations.append(
                    Violation(
                        rule_id="R001",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Bare collection type in signature: {node.name} (use strict_collections=False to disable)",
                    )
                )
                return

        if node.args.kwarg and node.args.kwarg.annotation:
            if AnnotationInspector.is_dict_str_any(node.args.kwarg.annotation):
                self.violations.append(
                    Violation(
                        rule_id="R001",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Dict[str, Any] in signature: {node.name}",
                    )
                )
                return
            elif (
                self.config.strict_collections
                and AnnotationInspector.is_bare_collection(node.args.kwarg.annotation)
            ):
                self.violations.append(
                    Violation(
                        rule_id="R001",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Bare collection type in signature: {node.name} (use strict_collections=False to disable)",
                    )
                )
                return

        if node.returns:
            if AnnotationInspector.is_dict_str_any(node.returns):
                self.violations.append(
                    Violation(
                        rule_id="R001",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Dict[str, Any] in signature: {node.name}",
                    )
                )
            elif (
                self.config.strict_collections
                and AnnotationInspector.is_bare_collection(node.returns)
            ):
                self.violations.append(
                    Violation(
                        rule_id="R001",
                        severity=RuleSeverity.HIGH,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Bare collection type in signature: {node.name} (use strict_collections=False to disable)",
                    )
                )

        self.generic_visit(node)
