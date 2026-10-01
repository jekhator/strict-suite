"""Linter object definitions."""

from dataclasses import dataclass


class BaselineLoadError(ValueError):
    """Error loading or parsing baseline file."""


@dataclass(frozen=True, slots=True)
class BaselineEntry:
    """Baseline entry for tracking accepted violations."""

    file: str
    line: int
    rule_id: str
    message_hash: str
