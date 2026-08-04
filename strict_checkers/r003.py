"""Checker for R003: Dataclass uses anti-canonical repr=False."""

import ast
import logging
from pathlib import Path

from strict_checkers.base import BaseChecker
from strict_config._config import Config
from strict_inspection import PathClassifier
from strict_rules import RuleSeverity, Violation

ERR_R003_ALLOWLIST_UNDETECTED = (
    "Class {class_name} is in r003_sensitivity_allowlist but no sensitivity "
    "base or field metadata detected. Config may be stale."
)

logger = logging.getLogger(__name__)


class R003Checker(BaseChecker):
    """Check for dataclass decorator without frozen+slots+repr=False."""

    def __init__(self, file_path: Path, source: str, config: Config):
        super().__init__(file_path, source, config)
        self.in_dto_file = False
        self.in_dto_file = PathClassifier.is_dto_path(file_path, config.dto_paths)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        if not self.in_dto_file:
            self.generic_visit(node)
            return

        if self.is_suppressed(node, "R003"):
            self.generic_visit(node)
            return

        for decorator in node.decorator_list:
            if self._is_dataclass_decorator(decorator):
                kwargs = self._extract_decorator_kwargs(decorator)

                if self.config.r003_mode == "canonical":
                    if self.config.r003_strict_repr:
                        has_repr_false = kwargs.get("repr") == "False"
                        if has_repr_false and not self._is_sensitivity_aware_repr_false(
                            node
                        ):
                            self.violations.append(
                                Violation(
                                    rule_id="R003",
                                    severity=RuleSeverity.MEDIUM,
                                    file=str(self.file_path),
                                    line=node.lineno,
                                    col=node.col_offset,
                                    message=f"@dataclass uses anti-canonical repr=False: {node.name}. Remove it.",
                                )
                            )
                    else:
                        has_frozen = kwargs.get("frozen") == "True"
                        has_slots = kwargs.get("slots") == "True"

                        if not (has_frozen and has_slots):
                            missing = []
                            if not has_frozen:
                                missing.append("frozen=True")
                            if not has_slots:
                                missing.append("slots=True")

                            self.violations.append(
                                Violation(
                                    rule_id="R003",
                                    severity=RuleSeverity.MEDIUM,
                                    file=str(self.file_path),
                                    line=node.lineno,
                                    col=node.col_offset,
                                    message=f"@dataclass missing {', '.join(missing)}: {node.name}",
                                )
                            )
                else:
                    has_frozen = kwargs.get("frozen") == "True"
                    has_slots = kwargs.get("slots") == "True"
                    has_repr_false = kwargs.get("repr") == "False"

                    if not (has_frozen and has_slots and has_repr_false):
                        missing = []
                        if not has_frozen:
                            missing.append("frozen=True")
                        if not has_slots:
                            missing.append("slots=True")
                        if not has_repr_false:
                            missing.append("repr=False")

                        self.violations.append(
                            Violation(
                                rule_id="R003",
                                severity=RuleSeverity.MEDIUM,
                                file=str(self.file_path),
                                line=node.lineno,
                                col=node.col_offset,
                                message=f"@dataclass missing {', '.join(missing)}: {node.name}",
                            )
                        )

        self.generic_visit(node)

    def _is_sensitivity_aware_repr_false(self, node: ast.ClassDef) -> bool:
        """Check if repr=False is allowed due to sensitivity mixin or metadata."""
        full_class_path = f"{self.file_path.stem}.{node.name}"

        if node.name in self.config.r003_sensitivity_allowlist:
            has_sensitivity = self._has_sensitivity_base(
                node
            ) or self._has_sensitivity_field_metadata(node)
            if not has_sensitivity:
                logger.info(ERR_R003_ALLOWLIST_UNDETECTED.format(class_name=node.name))
            return True

        if full_class_path in self.config.r003_sensitivity_allowlist:
            has_sensitivity = self._has_sensitivity_base(
                node
            ) or self._has_sensitivity_field_metadata(node)
            if not has_sensitivity:
                logger.info(
                    ERR_R003_ALLOWLIST_UNDETECTED.format(class_name=full_class_path)
                )
            return True

        if self._has_sensitivity_base(node):
            return True

        if self._has_sensitivity_field_metadata(node):
            return True

        return False

    def _has_sensitivity_base(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from a sensitivity mixin base."""
        for base in node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr

            if base_name in self.config.r003_sensitivity_bases:
                return True

        return False

    def _has_sensitivity_field_metadata(self, node: ast.ClassDef) -> bool:
        """Check if any field has sensitivity metadata."""
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.value, ast.Call):
                    if isinstance(item.value.func, ast.Name):
                        if item.value.func.id == "field":
                            for keyword in item.value.keywords:
                                if keyword.arg == "metadata":
                                    if self._metadata_contains_sensitivity_key(
                                        keyword.value
                                    ):
                                        return True

        return False

    def _metadata_contains_sensitivity_key(self, metadata_node: ast.expr) -> bool:
        """Check if metadata dict contains 'sensitivity' key."""
        if not isinstance(metadata_node, ast.Dict):
            return False

        for key in metadata_node.keys:
            if isinstance(key, ast.Constant):
                if key.value == "sensitivity":
                    return True

        return False

    def _is_dataclass_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is @dataclass."""
        if isinstance(decorator, ast.Name):
            return decorator.id == "dataclass"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id == "dataclass"
        return False

    def _extract_decorator_kwargs(self, decorator: ast.expr) -> dict[str, str]:
        """Extract kwargs from @dataclass(...) decorator."""
        kwargs: dict[str, str] = {}
        if isinstance(decorator, ast.Call):
            for keyword in decorator.keywords:
                if keyword.arg is None:
                    continue
                if isinstance(keyword.value, ast.Constant):
                    kwargs[keyword.arg] = str(keyword.value.value)
                elif isinstance(keyword.value, ast.NameConstant):
                    kwargs[keyword.arg] = str(keyword.value.value)
                elif isinstance(keyword.value, ast.Name):
                    kwargs[keyword.arg] = keyword.value.id
        return kwargs
