"""Base class for AST checkers."""

import ast
from pathlib import Path

from strict_config._config import Config
from strict_inspection import AnnotationInspector
from strict_rules import Violation


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

    def has_exception_tag(self, node: ast.FunctionDef) -> bool:
        """Check the def line and the first docstring line for a configured exception tag, case-insensitively."""
        texts = [self.get_comment_text(node.lineno)]
        docstring = ast.get_docstring(node)
        if docstring:
            texts.append(docstring.partition("\n")[0])
        lowered = [text.lower() for text in texts if text]
        return any(
            tag.lower() in text for tag in self.config.exception_tags for text in lowered
        )

    def is_suppressed(self, node: ast.AST, rule_id: str) -> bool:
        """Check if node has a noqa comment suppressing the given rule."""
        return AnnotationInspector.has_noqa_comment(node, rule_id, self.lines)
