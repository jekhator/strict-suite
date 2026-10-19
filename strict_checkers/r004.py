"""Checker for R004: Module-level facade, a wrapper that only delegates to a class method."""

import ast
from pathlib import Path

from strict_checkers.base import BaseChecker
from strict_config._config import Config
from strict_inspection import PathClassifier
from strict_rules import RuleSeverity, Violation


class R004Checker(BaseChecker):
    """Check for module-level facades in service paths.

    A facade is a module-level function whose body, after an optional docstring,
    is a single delegation to a class method (Name.method(...), Name(...).method(...),
    or an instance built and used on the next line) with no logic of its own.
    """

    def __init__(self, file_path: Path, source: str, config: Config):
        super().__init__(file_path, source, config)
        self.in_service_file = PathClassifier.is_service_path(
            file_path, config.service_paths
        )

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module to find top-level facade functions."""
        if not self.in_service_file:
            return

        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue

            if self.is_suppressed(item, "R004"):
                continue

            target = self._facade_target(item)
            if target is None:
                continue

            if self.has_exception_tag(item):
                continue

            class_name, method_name = target
            self.violations.append(
                Violation(
                    rule_id="R004",
                    severity=RuleSeverity.HIGH,
                    file=str(self.file_path),
                    line=item.lineno,
                    col=item.col_offset,
                    message=(
                        f"Facade '{item.name}': module-level wrapper around "
                        f"{class_name}.{method_name}; call the class method directly or "
                        "move the logic onto the class. A framework-required wrapper "
                        "carries an exception tag (for example '# FRAMEWORK')."
                    ),
                )
            )

    def _facade_target(self, node: ast.FunctionDef) -> tuple[str, str] | None:
        """Return (class name, method name) when the body is a bare class-method delegation."""
        body = node.body
        if body and self._is_docstring(body[0]):
            body = body[1:]

        if len(body) == 1:
            statement = body[0]
            if isinstance(statement, ast.Return) and statement.value is not None:
                return self._delegation_target(statement.value)
            if isinstance(statement, ast.Expr):
                return self._delegation_target(statement.value)
            return None

        if len(body) == 2:
            return self._instance_delegation_target(body[0], body[1])

        return None

    def _instance_delegation_target(
        self, assign: ast.stmt, ret: ast.stmt
    ) -> tuple[str, str] | None:
        """Return (class name, method name) for `instance = Name(...)` then `return instance.method(...)`."""
        if not (
            isinstance(assign, ast.Assign)
            and len(assign.targets) == 1
            and isinstance(assign.targets[0], ast.Name)
            and isinstance(assign.value, ast.Call)
        ):
            return None

        class_name = self._class_name(assign.value.func)
        if class_name is None or not isinstance(ret, ast.Return):
            return None

        call = ret.value
        if not (
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == assign.targets[0].id
        ):
            return None

        return class_name, call.func.attr

    def _delegation_target(self, expr: ast.expr) -> tuple[str, str] | None:
        """Return (class name, method name) for `Name.method(...)` or `Name(...).method(...)`."""
        if not (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute)):
            return None

        owner = expr.func.value
        class_name = self._class_name(owner)
        if class_name is None and isinstance(owner, ast.Call):
            class_name = self._class_name(owner.func)
        if class_name is None:
            return None

        return class_name, expr.func.attr

    @staticmethod
    def _class_name(node: ast.expr) -> str | None:
        """Return the identifier when the node is a capitalized name, the shape of a class reference."""
        if isinstance(node, ast.Name) and node.id[:1].isupper():
            return node.id
        return None

    @staticmethod
    def _is_docstring(statement: ast.stmt) -> bool:
        """Check whether a statement is a string-literal docstring expression."""
        return (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
