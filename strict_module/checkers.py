"""AST checker implementations for each rule."""

import ast
from pathlib import Path

from .config import Config
from .rules import (
    RuleSeverity,
    Violation,
    is_dict_str_any,
    is_bare_collection,
    contains_any,
    has_noqa_comment,
)


class BaseChecker(ast.NodeVisitor):
    """Base class for AST checkers."""

    def __init__(self, file_path: Path, source: str, config: Config):
        self.file_path = file_path
        self.source = source
        self.config = config
        self.violations: list[Violation] = []
        self.lines = source.splitlines()

    def get_comment_text(self, line_num: int) -> str:
        """Get comment text for a line."""
        if line_num <= 0 or line_num > len(self.lines):
            return ""
        line = self.lines[line_num - 1]
        if "#" in line:
            return line.split("#", 1)[1].strip()
        return ""

    def is_suppressed(self, node: ast.AST, rule_id: str) -> bool:
        """Check if node has a noqa comment suppressing the given rule."""
        return has_noqa_comment(node, rule_id, self.lines)


class R001Checker(BaseChecker):
    """Check for Dict[str, Any] or bare collections in service-layer function signatures."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        from .rules import is_service_path

        if not is_service_path(self.file_path, self.config.service_paths):
            return

        # Check if rule is suppressed on this node
        if self.is_suppressed(node, "R001"):
            return

        # Check parameters
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation:
                if is_dict_str_any(arg.annotation):
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
                elif self.config.strict_collections and is_bare_collection(
                    arg.annotation
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

        # Check varargs and kwargs
        if node.args.vararg and node.args.vararg.annotation:
            if is_dict_str_any(node.args.vararg.annotation):
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
            elif self.config.strict_collections and is_bare_collection(
                node.args.vararg.annotation
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
            if is_dict_str_any(node.args.kwarg.annotation):
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
            elif self.config.strict_collections and is_bare_collection(
                node.args.kwarg.annotation
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

        # Check return type
        if node.returns:
            if is_dict_str_any(node.returns):
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
            elif self.config.strict_collections and is_bare_collection(node.returns):
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


class R002Checker(BaseChecker):
    """Check for inline dict literals with 3+ string keys."""

    def __init__(self, file_path: Path, source: str, config: Config):
        super().__init__(file_path, source, config)
        self.in_service_file = False
        self.tag_count = 0
        self.current_function: ast.FunctionDef | None = None
        self.current_class: ast.ClassDef | None = (
            None  # Track current class for to_* serializer detection
        )
        self.function_comments: dict[int, str | None] = {}
        self.dict_parents: dict[int, ast.AST] = {}  # Map dict node id to parent node
        from .rules import is_service_path

        self.in_service_file = is_service_path(file_path, config.service_paths)

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

        # Check if parent is AnnAssign (annotated assignment)
        if isinstance(parent, ast.AnnAssign):
            # Check if dict is the assigned value
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

        # Must be in a dataclass
        if not self._is_class_decorated_with_dataclass(self.current_class):
            return False

        # Must be in a to_* method
        if self.current_function is None or not self.current_function.name.startswith(
            "to_"
        ):
            return False

        # Check if the dict is inside a return statement of the current function
        for stmt in ast.walk(self.current_function):
            if isinstance(stmt, ast.Return) and stmt.value:
                # Check if dict_node is inside the return value
                for child in ast.walk(stmt.value):
                    if child is dict_node:
                        return True

        return False

    def visit_Dict(self, node: ast.Dict) -> None:
        """Visit dict literals."""
        if not self.in_service_file:
            self.generic_visit(node)
            return

        # Check if rule is suppressed on this node
        if self.is_suppressed(node, "R002"):
            self.generic_visit(node)
            return

        # SKIP: Annotated module/class-level constants (typed declarations)
        # These are like: DISPLAY_LABELS: dict[str, str] = {...}
        # The explicit type annotation signals intent ('typed static data'),
        # distinct from inline business-shape literals in function bodies.
        if self._is_annotated_constant(node):
            self.generic_visit(node)
            return

        # SKIP: Dict literals returned from to_* methods in dataclasses
        # These are serializer outputs, not unconverted business shapes.
        # Example: a DTO's to_dict() method returns a 3+-key dict for serialization.
        if self._is_serializer_return_dict(node):
            self.generic_visit(node)
            return

        # Count string keys
        string_keys = sum(
            1
            for key in node.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        )

        # Skip trivial dicts and unpacking dicts (use configurable threshold)
        if (
            string_keys >= self.config.min_dict_keys
            and len(node.keys) >= self.config.min_dict_keys
        ):
            # Check for exception tag on dict line or function line
            comment = self.get_comment_text(node.lineno)
            if not comment and self.current_function:
                comment = self.function_comments.get(id(self.current_function)) or ""

            has_tag = any(tag in comment for tag in self.config.exception_tags)

            if has_tag:
                # Validate justification if required
                if self.config.exception_tag_requires_justification:
                    # Tag must include a colon followed by justification
                    has_justification = False
                    for tag in self.config.exception_tags:
                        if tag in comment:
                            # Check if there's a colon and text after the tag
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
                                message="Exception tag missing justification. Format: 'tag: explanation' (e.g., 'facade — celery schedule: transient event payload')",
                            )
                        )
                        self.generic_visit(node)
                        return

                # Track tag usage if max_exception_tags_per_file is set
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
                # No tag: flag the dict
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


class R003Checker(BaseChecker):
    """Check for dataclass decorator without frozen+slots+repr=False."""

    def __init__(self, file_path: Path, source: str, config: Config):
        super().__init__(file_path, source, config)
        self.in_dto_file = False
        from .rules import is_dto_path

        self.in_dto_file = is_dto_path(file_path, config.dto_paths)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        if not self.in_dto_file:
            self.generic_visit(node)
            return

        # Check if rule is suppressed on this node
        if self.is_suppressed(node, "R003"):
            self.generic_visit(node)
            return

        # Look for @dataclass decorator
        for decorator in node.decorator_list:
            if self._is_dataclass_decorator(decorator):
                kwargs = self._extract_decorator_kwargs(decorator)

                # In canonical mode (v0.2 default): flag repr=False (anti-canonical) if strict_repr=True
                if self.config.r003_mode == "canonical":
                    if self.config.r003_strict_repr:
                        has_repr_false = kwargs.get("repr") == "False"
                        if has_repr_false:
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
                        # Relaxed mode: only check frozen+slots, ignore repr=False
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
                # In legacy mode (v0.1): flag missing repr=False
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


class R004Checker(BaseChecker):
    """Check for module-level functions without exception tags (auto-detects class-method wrappers)."""

    def __init__(self, file_path: Path, source: str, config: Config):
        super().__init__(file_path, source, config)
        self.in_service_file = False
        from .rules import is_service_path

        self.in_service_file = is_service_path(file_path, config.service_paths)

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module to find top-level function defs."""
        if not self.in_service_file:
            return

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Check if rule is suppressed on this node
                if self.is_suppressed(item, "R004"):
                    continue
                if not self._has_exception_tag(
                    item
                ) and not self._is_class_method_wrapper(item):
                    self.violations.append(
                        Violation(
                            rule_id="R004",
                            severity=RuleSeverity.HIGH,
                            file=str(self.file_path),
                            line=item.lineno,
                            col=item.col_offset,
                            message=f"Module-level def without exception tag: {item.name}",
                        )
                    )

    def _is_class_method_wrapper(self, node: ast.FunctionDef) -> bool:
        """Check if function body delegates to class methods (auto-detected wrapper pattern)."""
        for stmt in node.body:
            if isinstance(stmt, ast.Return) and stmt.value:
                # Check if return value is a call to a class/instance method
                if self._is_method_delegation(stmt.value):
                    return True
        return False

    def _is_method_delegation(self, node: ast.expr) -> bool:
        """Check if node is a method call (attribute access followed by call)."""
        if isinstance(node, ast.Call):
            func = node.func
            # Pattern: obj.method(...) or obj.attr.method(...)
            if isinstance(func, ast.Attribute):
                return True
        return False

    def _has_exception_tag(self, node: ast.FunctionDef) -> bool:
        """Check if function has a documented exception tag."""
        # Check inline comment on function line
        comment = self.get_comment_text(node.lineno)
        for tag in self.config.exception_tags:
            if tag in comment:
                return True

        # Check docstring first line
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring = node.body[0].value.value
            for tag in self.config.exception_tags:
                if tag in docstring:
                    return True

        return False


class R005Checker(BaseChecker):
    """Check for validators using DTO.from_dict() pattern."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        # Only check functions starting with validate_
        if not node.name.startswith("validate_"):
            self.generic_visit(node)
            return

        # Check if rule is suppressed on this node
        if self.is_suppressed(node, "R005"):
            self.generic_visit(node)
            return

        # Check if it has a 'payload' parameter
        has_payload_param = any(
            arg.arg == "payload" for arg in node.args.args + node.args.kwonlyargs
        )

        if not has_payload_param:
            self.generic_visit(node)
            return

        # Check for DTO.from_dict() or ValidationError in function body
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


class R006Checker(BaseChecker):
    """Check for typing.Any in service-layer function signatures."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        from .rules import is_service_path

        # Test files are always exempt from R006
        if not is_service_path(self.file_path, self.config.r006_paths):
            self.generic_visit(node)
            return

        # Check if rule is suppressed on this node
        if self.is_suppressed(node, "R006"):
            self.generic_visit(node)
            return

        # Check parameters
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation and contains_any(arg.annotation):
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

        # Check varargs and kwargs
        if node.args.vararg and node.args.vararg.annotation:
            if contains_any(node.args.vararg.annotation):
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
            if contains_any(node.args.kwarg.annotation):
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

        # Check return type
        if node.returns and contains_any(node.returns):
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


class R007Checker(BaseChecker):
    """Check for pytest fixtures defined outside conftest.py."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to find pytest fixtures."""
        from .rules import is_test_file

        # Only check test files
        if not is_test_file(self.file_path):
            self.generic_visit(node)
            return

        # conftest.py is allowed to have fixtures
        if self.file_path.name == "conftest.py":
            self.generic_visit(node)
            return

        # Check if function has @pytest.fixture decorator
        for decorator in node.decorator_list:
            if self._is_pytest_fixture_decorator(decorator):
                # Check if rule is suppressed on this node
                if self.is_suppressed(node, "R007"):
                    continue

                self.violations.append(
                    Violation(
                        rule_id="R007",
                        severity=RuleSeverity.MEDIUM,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Pytest fixture defined outside conftest.py: {node.name}. Move to conftest.py.",
                    )
                )

        self.generic_visit(node)

    def _is_pytest_fixture_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is @pytest.fixture."""
        # Match: @pytest.fixture or @fixture (if imported)
        if isinstance(decorator, ast.Name):
            return decorator.id == "fixture"
        elif isinstance(decorator, ast.Attribute):
            # Match: @pytest.fixture
            if decorator.attr == "fixture":
                if isinstance(decorator.value, ast.Name):
                    if decorator.value.id == "pytest":
                        return True
        elif isinstance(decorator, ast.Call):
            # Match: @pytest.fixture() or @fixture()
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id == "fixture"
            elif isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr == "fixture":
                    if isinstance(decorator.func.value, ast.Name):
                        if decorator.func.value.id == "pytest":
                            return True
        return False


class R008Checker(BaseChecker):
    """Check for bare module-level test functions."""

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module to find top-level test functions."""
        from .rules import is_test_file

        # Only check test files
        if not is_test_file(self.file_path):
            return

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Check if function name starts with test_
                if item.name.startswith("test_"):
                    # Check if rule is suppressed on this node
                    if self.is_suppressed(item, "R008"):
                        continue

                    self.violations.append(
                        Violation(
                            rule_id="R008",
                            severity=RuleSeverity.MEDIUM,
                            file=str(self.file_path),
                            line=item.lineno,
                            col=item.col_offset,
                            message=f"Module-level test function: {item.name}. Move into Test<Concern> class.",
                        )
                    )
