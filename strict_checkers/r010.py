"""Checker for R010: Legacy typing aliases for abstract base classes."""

import ast

from strict_checkers.base import BaseChecker
from strict_rules import RuleSeverity

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


class R010Checker(BaseChecker):
    """Check for legacy typing.* ABCs that should use collections.abc."""

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit 'from' imports to find typing.* ABC imports."""
        if node.module == "typing" and not self.is_suppressed(node, "R010"):
            for alias in node.names:
                if alias.name in LEGACY_TO_MODERN:
                    self.add_violation(
                        rule_id="R010",
                        severity=RuleSeverity.MEDIUM,
                        line=node.lineno,
                        col=node.col_offset,
                        message=f"Import '{alias.name}' from typing, not collections.abc. Use 'from collections.abc import {alias.name}' instead.",
                    )

        self.generic_visit(node)
