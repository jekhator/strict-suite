"""Rule definitions for strict-module linter (formerly dto-strict)."""

import ast
import fnmatch
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class RuleSeverity(Enum):
    """Severity levels for violations."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True, slots=True)
class Violation:
    """Represents a single linting violation."""

    rule_id: str
    severity: RuleSeverity
    file: str
    line: int
    col: int
    message: str

    def format_text(self) -> str:
        """Format as plain text."""
        return f"{self.file}:{self.line}: {self.rule_id} {self.message}"

    def format_github(self) -> str:
        """Format as GitHub Actions annotation."""
        level = "error" if self.severity == RuleSeverity.HIGH else "warning"
        return f"::{level} file={self.file},line={self.line},col={self.col}::{self.message}"


@dataclass(frozen=True, slots=True)
class Rule:
    """Rule definition."""

    id: str
    name: str
    severity: RuleSeverity
    description: str


class RuleRegistry:
    """Registry of all linting rules."""

    RULES = {
        "R001": Rule(
            "R001",
            "Dict[str, Any] or bare collections in service signatures",
            RuleSeverity.HIGH,
            "Function signature contains Dict[str, Any], bare dict, list, or tuple without type parameters.",
        ),
        "R002": Rule(
            "R002",
            "Inline dict literals with 3+ keys",
            RuleSeverity.MEDIUM,
            "Inline dict literal with multiple string keys; consider converting to DTO.",
        ),
        "R003": Rule(
            "R003",
            "Dataclass uses anti-canonical repr=False",
            RuleSeverity.MEDIUM,
            "Dataclass uses anti-canonical repr=False. Per strict-module canonical (v0.2): plain @dataclass(frozen=True, slots=True). Remove repr=False.",
        ),
        "R004": Rule(
            "R004",
            "Module-level function without exception tag",
            RuleSeverity.HIGH,
            "Module-level function definition lacks documented exception tag (facade pattern).",
        ),
        "R005": Rule(
            "R005",
            "Validator not using DTO.from_dict() pattern",
            RuleSeverity.LOW,
            "Validator function should use DTO.from_dict() to validate payload shape.",
        ),
        "R006": Rule(
            "R006",
            "typing.Any in signature",
            RuleSeverity.HIGH,
            "Function signature contains typing.Any in parameter or return type. Use forward refs (TYPE_CHECKING) for class types, narrow protocols (IO[bytes]) for file objects, or build a proper DTO for business shapes.",
        ),
        "R007": Rule(
            "R007",
            "Pytest fixtures defined outside conftest.py",
            RuleSeverity.MEDIUM,
            "Pytest fixture @pytest.fixture decorator found in non-conftest file. Fixtures must be defined in conftest.py.",
        ),
        "R008": Rule(
            "R008",
            "Bare module-level test function",
            RuleSeverity.MEDIUM,
            "Module-level test function def test_*() found. Test functions must be defined as methods in Test<Concern> classes.",
        ),
    }

    @classmethod
    def get_rule(cls, rule_id: str) -> Optional[Rule]:
        """Get rule by ID."""
        return cls.RULES.get(rule_id)


def is_test_file(file_path: Path) -> bool:
    """Check if file is a test file by basename (conftest.py or test_*.py) for linting."""
    basename = file_path.name

    # Check basename patterns
    if basename == "conftest.py" or basename.startswith("test_"):
        return True

    return False


def is_loc_test_file(file_path: Path) -> bool:
    """Check if file is a test file (conftest.py, test_*.py, or under tests/ directory)."""
    basename = file_path.name

    # Check basename patterns
    if basename == "conftest.py" or basename.startswith("test_"):
        return True

    # Check if under a tests/ directory
    if "/tests/" in str(file_path) or str(file_path).startswith("tests/"):
        return True

    return False


def is_service_path(file_path: Path, service_paths: list[str]) -> bool:
    """Check if file path matches a service path pattern (excluding test files)."""
    # Test files are always exempt
    if is_test_file(file_path):
        return False

    for pattern in service_paths:
        if fnmatch.fnmatch(str(file_path), pattern):
            return True
    return False


def is_dto_path(file_path: Path, dto_paths: list[str]) -> bool:
    """Check if file path matches a DTO path pattern (excluding test files)."""
    # Test files are always exempt
    if is_test_file(file_path):
        return False

    for pattern in dto_paths:
        if fnmatch.fnmatch(str(file_path), pattern):
            return True
    return False


def has_noqa_comment(node: ast.AST, rule_id: str, source_lines: list[str]) -> bool:
    """Check if node's line has a noqa comment suppressing the given rule (supports backward-compat dto-strict tags)."""
    if not hasattr(node, "lineno") or node.lineno is None:
        return False
    if node.lineno > len(source_lines):
        return False

    line = source_lines[node.lineno - 1]

    # Check if line contains a noqa comment
    if "#" not in line:
        return False

    # Find the comment part (after #)
    comment_idx = line.find("#")
    comment_part = line[comment_idx + 1 :].strip()

    # Check if the comment contains "noqa"
    if not comment_part.startswith("noqa"):
        return False

    noqa_part = comment_part[4:].strip()  # Skip "noqa" (4 chars)

    # Bare noqa (without codes) suppresses all rules
    if not noqa_part or noqa_part.startswith("#") or noqa_part.startswith("-"):
        return True

    # Check for colon-based specs
    if noqa_part.startswith(":"):
        spec = noqa_part[1:].strip()
        # Remove any trailing comment (# indicates start of new comment)
        if "#" in spec:
            spec = spec.split("#")[0].strip()

        # Remove any trailing dash-delimited explanation (e.g., "- explanation")
        parts = spec.split()
        if len(parts) > 1:
            # Check if second part starts with any dash character (-, en-dash, em-dash, etc.)
            second = parts[1]
            if second and second[0] in "-–—":
                # Trailing dash indicates explanation after the spec
                spec = parts[0]

        # "strict-module" suppresses all strict-module rules
        if spec == "strict-module":
            return True

        # "strict-module-R001" suppresses R001 specifically
        if spec == f"strict-module-{rule_id}":
            return True

        # "dto-strict" suppresses all rules (backward-compat)
        if spec == "dto-strict":
            return True

        # "dto-strict-R001" suppresses R001 (backward-compat)
        if spec == f"dto-strict-{rule_id}":
            return True

        # Handle comma-separated list (both new and old names)
        tokens = [t.strip() for t in spec.split(",")]
        if f"strict-module-{rule_id}" in tokens or f"dto-strict-{rule_id}" in tokens:
            return True

    return False


def get_annotation_string(annotation: Optional[ast.expr]) -> str:
    """Convert annotation AST node to string representation."""
    if annotation is None:
        return ""

    if isinstance(annotation, ast.Name):
        return annotation.id
    elif isinstance(annotation, ast.Subscript):
        base = get_annotation_string(annotation.value)
        if hasattr(ast, "Index") and isinstance(
            annotation.slice, ast.Index
        ):  # pragma: no cover
            # Python 3.8 compatibility
            index = get_annotation_string(annotation.slice.value)  # type: ignore[attr-defined]
        else:
            index = get_annotation_string(annotation.slice)
        return f"{base}[{index}]"
    elif isinstance(annotation, ast.Tuple):
        elements = ", ".join(get_annotation_string(e) for e in annotation.elts)
        return f"({elements})"
    elif isinstance(annotation, ast.Attribute):
        value = get_annotation_string(annotation.value)
        return f"{value}.{annotation.attr}"
    elif isinstance(annotation, ast.Constant):
        return repr(annotation.value)
    else:  # pragma: no cover
        return ""


def is_dict_str_any(annotation: Optional[ast.expr]) -> bool:
    """Check if annotation is Dict[str, Any] or dict[str, Any]."""
    if annotation is None:
        return False

    # Use ast.unparse for more reliable type detection
    try:
        ann_str = ast.unparse(annotation)
    except Exception:  # pragma: no cover
        return False

    ann_lower = ann_str.lower().replace(" ", "")

    # Check for typing.Dict[str, Any], Dict[str, Any], dict[str, Any]
    return "dict[str,any]" in ann_lower


def is_bare_collection(annotation: Optional[ast.expr]) -> bool:
    """Check if annotation is bare dict, list, or tuple without type parameters."""
    if annotation is None:
        return False

    # Only Name nodes without subscripts are bare collections
    if isinstance(annotation, ast.Name):
        return annotation.id in ("dict", "list", "tuple")

    return False


def contains_any(annotation: Optional[ast.expr]) -> bool:
    """Check if annotation contains typing.Any."""
    if annotation is None:
        return False

    try:
        ann_str = ast.unparse(annotation)
    except Exception:  # pragma: no cover
        return False

    ann_lower = ann_str.lower().replace(" ", "")

    # Check for Any in various forms: Any, Optional[Any], list[Any], dict[str, Any], etc.
    return "any" in ann_lower
