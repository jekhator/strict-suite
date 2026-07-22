"""LOC cap configuration."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocCapConfig:
    """Configuration for LOC cap checker."""

    hard_cap: int = 694
    soft_target: int = 500
    baseline_file: str = ".loc-cap-baseline.txt"
    exclude_patterns: tuple[str, ...] = ("migrations", "management/commands")
