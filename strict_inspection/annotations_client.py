"""Annotation and noqa comment inspection utilities."""

import ast

from strict_config.constants import (
    BARE_COLLECTION_TYPES,
    NOQA_KEYWORD,
    PREFIX_DTO_STRICT,
    PREFIX_STRICT_MODULE,
)

DICT_TYPE_NAMES = ("dict",)
STR_TYPE_NAME = "str"
ANY_TYPE_NAME = "any"
NOQA_SEPARATORS = "-–—"


class AnnotationInspector:
    """Inspect Python annotations and noqa comments."""

    @staticmethod
    def get_annotation_string(annotation: ast.expr | None) -> str:
        """Convert annotation AST node to string representation."""
        if annotation is None:
            return ""

        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Subscript):
            base = AnnotationInspector.get_annotation_string(annotation.value)
            index = AnnotationInspector.get_annotation_string(annotation.slice)
            return f"{base}[{index}]"
        if isinstance(annotation, ast.Tuple):
            elements = ", ".join(
                AnnotationInspector.get_annotation_string(e) for e in annotation.elts
            )
            return f"({elements})"
        if isinstance(annotation, ast.Attribute):
            value = AnnotationInspector.get_annotation_string(annotation.value)
            return f"{value}.{annotation.attr}"
        if isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        return ""

    @staticmethod
    def is_dict_str_any(annotation: ast.expr | None) -> bool:
        """Check if an annotation contains Dict[str, Any] or dict[str, Any], qualified or not."""
        if annotation is None:
            return False

        return any(
            isinstance(node, ast.Subscript)
            and AnnotationInspector._tail_name(node.value).lower() in DICT_TYPE_NAMES
            and isinstance(node.slice, ast.Tuple)
            and len(node.slice.elts) == 2
            and AnnotationInspector._tail_name(node.slice.elts[0]).lower() == STR_TYPE_NAME
            and AnnotationInspector._tail_name(node.slice.elts[1]).lower() == ANY_TYPE_NAME
            for node in ast.walk(annotation)
        )

    @staticmethod
    def is_bare_collection(annotation: ast.expr | None) -> bool:
        """Check if annotation is bare dict, list, or tuple without type parameters."""
        if isinstance(annotation, ast.Name):
            return annotation.id in BARE_COLLECTION_TYPES
        return False

    @staticmethod
    def contains_any(annotation: ast.expr | None) -> bool:
        """Check if an annotation names typing.Any, bare or qualified, anywhere inside it."""
        if annotation is None:
            return False

        return any(
            (isinstance(node, ast.Name) and node.id == "Any")
            or (isinstance(node, ast.Attribute) and node.attr == "Any")
            for node in ast.walk(annotation)
        )

    @staticmethod
    def has_noqa_comment(node: ast.AST, rule_id: str, source_lines: list[str]) -> bool:
        """Check if node's line has a noqa comment suppressing the given rule (supports backward-compat dto-strict tags and bare rule codes)."""
        line_number = getattr(node, "lineno", None)
        if line_number is None or line_number > len(source_lines):
            return False

        line = source_lines[line_number - 1]
        if "#" not in line:
            return False

        comment_part = line[line.find("#") + 1 :].strip()
        if not comment_part.startswith(NOQA_KEYWORD):
            return False

        noqa_part = comment_part[len(NOQA_KEYWORD) :].strip()
        if not noqa_part or noqa_part.startswith(("#", "-")):
            return True

        if not noqa_part.startswith(":"):
            return False

        spec = noqa_part[1:].strip()
        if "#" in spec:
            spec = spec.split("#")[0].strip()

        parts = spec.split()
        if len(parts) > 1 and parts[1][:1] and parts[1][0] in NOQA_SEPARATORS:
            spec = parts[0]

        if spec in (PREFIX_STRICT_MODULE, PREFIX_DTO_STRICT):
            return True

        if spec in (
            f"{PREFIX_STRICT_MODULE}-{rule_id}",
            f"{PREFIX_DTO_STRICT}-{rule_id}",
        ):
            return True

        tokens = [t.strip() for t in spec.split(",")]
        return (
            f"{PREFIX_STRICT_MODULE}-{rule_id}" in tokens
            or f"{PREFIX_DTO_STRICT}-{rule_id}" in tokens
            or rule_id in tokens
        )

    @staticmethod
    def _tail_name(node: ast.expr) -> str:
        """Return the identifier of a Name or the attribute of an Attribute, or an empty string."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""
