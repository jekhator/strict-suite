"""Linter object definitions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BaselineEntry:
    """Baseline entry for tracking accepted violations."""

    file: str
    line: int
    rule_id: str
    message_hash: str
