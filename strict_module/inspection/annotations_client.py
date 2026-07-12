"""Annotation and noqa comment inspection utilities."""

import ast
from typing import Optional


class AnnotationInspector:
    """Inspect Python annotations and noqa comments."""

    @staticmethod
    def get_annotation_string(annotation: Optional[ast.expr]) -> str:
        """Convert annotation AST node to string representation."""
        if annotation is None:
            return ""

        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            base = AnnotationInspector.get_annotation_string(annotation.value)
            if hasattr(ast, "Index") and isinstance(annotation.slice, ast.Index):
                index = AnnotationInspector.get_annotation_string(
                    annotation.slice.value
                )  # type: ignore[attr-defined]
            else:
                index = AnnotationInspector.get_annotation_string(annotation.slice)
            return f"{base}[{index}]"
        elif isinstance(annotation, ast.Tuple):
            elements = ", ".join(
                AnnotationInspector.get_annotation_string(e) for e in annotation.elts
            )
            return f"({elements})"
        elif isinstance(annotation, ast.Attribute):
            value = AnnotationInspector.get_annotation_string(annotation.value)
            return f"{value}.{annotation.attr}"
        elif isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        else:
            return ""

    @staticmethod
    def is_dict_str_any(annotation: Optional[ast.expr]) -> bool:
        """Check if annotation is Dict[str, Any] or dict[str, Any]."""
        if annotation is None:
            return False

        try:
            ann_str = ast.unparse(annotation)
        except Exception:
            return False

        ann_lower = ann_str.lower().replace(" ", "")
        return "dict[str,any]" in ann_lower

    @staticmethod
    def is_bare_collection(annotation: Optional[ast.expr]) -> bool:
        """Check if annotation is bare dict, list, or tuple without type parameters."""
        if annotation is None:
            return False

        if isinstance(annotation, ast.Name):
            return annotation.id in ("dict", "list", "tuple")

        return False

    @staticmethod
    def contains_any(annotation: Optional[ast.expr]) -> bool:
        """Check if annotation contains typing.Any."""
        if annotation is None:
            return False

        try:
            ann_str = ast.unparse(annotation)
        except Exception:
            return False

        ann_lower = ann_str.lower().replace(" ", "")
        return "any" in ann_lower

    @staticmethod
    def has_noqa_comment(node: ast.AST, rule_id: str, source_lines: list[str]) -> bool:
        """Check if node's line has a noqa comment suppressing the given rule (supports backward-compat dto-strict tags)."""
        if not hasattr(node, "lineno") or node.lineno is None:
            return False
        if node.lineno > len(source_lines):
            return False

        line = source_lines[node.lineno - 1]

        if "#" not in line:
            return False

        comment_idx = line.find("#")
        comment_part = line[comment_idx + 1 :].strip()

        if not comment_part.startswith("noqa"):
            return False

        noqa_part = comment_part[4:].strip()

        if not noqa_part or noqa_part.startswith("#") or noqa_part.startswith("-"):
            return True

        if noqa_part.startswith(":"):
            spec = noqa_part[1:].strip()
            if "#" in spec:
                spec = spec.split("#")[0].strip()

            parts = spec.split()
            if len(parts) > 1:
                second = parts[1]
                if second and second[0] in "-–—":
                    spec = parts[0]

            if spec == "strict-module":
                return True

            if spec == f"strict-module-{rule_id}":
                return True

            if spec == "dto-strict":
                return True

            if spec == f"dto-strict-{rule_id}":
                return True

            tokens = [t.strip() for t in spec.split(",")]
            if (
                f"strict-module-{rule_id}" in tokens
                or f"dto-strict-{rule_id}" in tokens
            ):
                return True

        return False
