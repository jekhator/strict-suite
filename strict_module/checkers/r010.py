"""Checker for R010: Legacy typing aliases for abstract base classes."""

import ast

from strict_module.checkers.base import BaseChecker
from strict_module.rules import RuleSeverity, Violation


class R010Checker(BaseChecker):
    """Check for legacy typing.* ABCs that should use collections.abc."""

    LEGACY_TO_MODERN = {
        "Callable": "collections.abc.Callable",
        "Iterable": "collections.abc.Iterable",
        "Iterator": "collections.abc.Iterator",
        "Awaitable": "collections.abc.Awaitable",
        "AsyncIterable": "collections.abc.AsyncIterable",
        "AsyncIterator": "collections.abc.AsyncIterator",
        "Mapping": "collections.abc.Mapping",
        "MutableMapping": "collections.abc.MutableMapping",
        "Sequence": "collections.abc.Sequence",
        "MutableSequence": "collections.abc.MutableSequence",
        "Set": "collections.abc.Set",
        "MutableSet": "collections.abc.MutableSet",
        "Hashable": "collections.abc.Hashable",
        "Sized": "collections.abc.Sized",
        "Container": "collections.abc.Container",
        "Collection": "collections.abc.Collection",
        "Reversible": "collections.abc.Reversible",
        "Generator": "collections.abc.Generator",
        "AsyncGenerator": "collections.abc.AsyncGenerator",
        "Coroutine": "collections.abc.Coroutine",
    }

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit 'from' imports to find typing.* ABC imports."""
        if node.module != "typing":
            self.generic_visit(node)
            return

        for alias in node.names:
            imported_name = alias.name
            if imported_name in self.LEGACY_TO_MODERN:
                if self.is_suppressed(node, "R010"):
                    self.generic_visit(node)
                    return

                self.violations.append(
                    Violation(
                        rule_id="R010",
                        severity=RuleSeverity.MEDIUM,
                        file=str(self.file_path),
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Import '{imported_name}' from typing, not collections.abc. Use 'from collections.abc import {imported_name}' instead.",
                    )
                )

        self.generic_visit(node)
