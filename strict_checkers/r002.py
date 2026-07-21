"""Checker for R002: Inline dict literals with 3+ keys."""

import ast
from pathlib import Path

from strict_checkers.base import BaseChecker
from strict_config._config import Config
from strict_inspection import PathClassifier
from strict_rules import RuleSeverity, Violation


class R002Checker(BaseChecker):
    """Check for inline dict literals with 3+ string keys."""

    def __init__(self, file_path: Path, source: str, config: Config):
        super().__init__(file_path, source, config)
        self.in_service_file = False
        self.tag_count = 0
        self.current_function: ast.FunctionDef | None = None
        self.current_class: ast.ClassDef | None = None
        self.function_comments: dict[int, str | None] = {}
        self.dict_parents: dict[int, ast.AST] = {}
        self.in_service_file = PathClassifier.is_service_path(
            file_path, config.service_paths
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class definitions to detect to_* serializer methods."""
        old_class = self.current_class
        self.current_class = node
        self._track_parents(node)
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function definitions to associate comments."""
        self.current_function = node
        comment = self.get_comment_text(node.lineno)
        self.function_comments[id(node)] = comment
        self.generic_visit(node)

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module to track parent relationships for dicts."""
        self._track_parents(node)
        self.generic_visit(node)

    def _track_parents(self, node: ast.AST) -> None:
        """Recursively track parent relationships for all dict nodes."""
        for child in ast.walk(node):
            for grandchild in ast.iter_child_nodes(child):
                if isinstance(grandchild, ast.Dict):
                    self.dict_parents[id(grandchild)] = child

    def _is_annotated_constant(self, dict_node: ast.Dict) -> bool:
        """Check if dict is a typed constant (inside AnnAssign at module/class level)."""
        parent = self.dict_parents.get(id(dict_node))
        if parent is None:
            return False

        if isinstance(parent, ast.AnnAssign):
            if parent.value is dict_node:
                return True

        return False

    def _is_dataclass_decorator(self, node: ast.expr) -> bool:
        """Check if decorator is @dataclass (any form)."""
        if isinstance(node, ast.Name):
            return node.id == "dataclass"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id == "dataclass"
        return False

    def _is_class_decorated_with_dataclass(self, class_node: ast.ClassDef) -> bool:
        """Check if class is decorated with @dataclass."""
        for decorator in class_node.decorator_list:
            if self._is_dataclass_decorator(decorator):
                return True
        return False

    def _is_serializer_return_dict(self, dict_node: ast.Dict) -> bool:
        """Check if dict is returned from a to_* serializer method in a dataclass."""
        if self.current_class is None:
            return False

        if not self._is_class_decorated_with_dataclass(self.current_class):
            return False

        if self.current_function is None or not self.current_function.name.startswith(
            "to_"
        ):
            return False

        for stmt in ast.walk(self.current_function):
            if isinstance(stmt, ast.Return) and stmt.value:
                for child in ast.walk(stmt.value):
                    if child is dict_node:
                        return True

        return False

    def visit_Dict(self, node: ast.Dict) -> None:
        """Visit dict literals."""
        if not self.in_service_file:
            self.generic_visit(node)
            return

        if self.is_suppressed(node, "R002"):
            self.generic_visit(node)
            return

        if self._is_annotated_constant(node):
            self.generic_visit(node)
            return

        if self._is_serializer_return_dict(node):
            self.generic_visit(node)
            return

        string_keys = sum(
            1
            for key in node.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        )

        if (
            string_keys >= self.config.min_dict_keys
            and len(node.keys) >= self.config.min_dict_keys
        ):
            comment = self.get_comment_text(node.lineno)
            if not comment and self.current_function:
                comment = self.function_comments.get(id(self.current_function)) or ""

            has_tag = any(tag in comment for tag in self.config.exception_tags)

            if has_tag:
                if self.config.exception_tag_requires_justification:
                    has_justification = False
                    for tag in self.config.exception_tags:
                        if tag in comment:
                            tag_idx = comment.find(tag)
                            after_tag = comment[tag_idx + len(tag) :].strip()
                            if after_tag.startswith(":") and len(after_tag) > 1:
                                has_justification = True
                                break

                    if not has_justification:
                        self.violations.append(
                            Violation(
                                rule_id="R002",
                                severity=RuleSeverity.MEDIUM,
                                file=str(self.file_path),
                                line=node.lineno,
                                col=node.col_offset,
                                message="Exception tag missing justification. Format: 'tag: explanation' (e.g., 'facade - celery schedule: transient event payload')",
                            )
                        )
                        self.generic_visit(node)
                        return

                if self.config.max_exception_tags_per_file is not None:
                    self.tag_count += 1
                    if self.tag_count > self.config.max_exception_tags_per_file:
                        self.violations.append(
                            Violation(
                                rule_id="R002",
                                severity=RuleSeverity.MEDIUM,
                                file=str(self.file_path),
                                line=node.lineno,
                                col=node.col_offset,
                                message=f"Exceeded max exception tags ({self.config.max_exception_tags_per_file}) in file",
                            )
                        )
            else:
                self.violations.append(
                    Violation(
                        rule_id="R002",
                        severity=RuleSeverity.MEDIUM,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Inline dict literal with {string_keys} keys (likely business-shape; convert to DTO)",
                    )
                )

        self.generic_visit(node)
