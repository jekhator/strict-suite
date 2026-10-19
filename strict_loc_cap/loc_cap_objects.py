"""LOC cap configuration."""

from dataclasses import dataclass

from strict_config.constants import (
    DEFAULT_EXCLUDE_PATTERNS,
    DEFAULT_LOC_CAP_BASELINE_FILE,
    DEFAULT_LOC_HARD_CAP,
    DEFAULT_LOC_SOFT_TARGET,
)


class LocCapInputError(ValueError):
    """A source file or baseline that the LOC cap cannot read."""


@dataclass(frozen=True, slots=True)
class LocCapConfig:
    """Configuration for LOC cap checker."""

    hard_cap: int = DEFAULT_LOC_HARD_CAP
    soft_target: int = DEFAULT_LOC_SOFT_TARGET
    baseline_file: str = DEFAULT_LOC_CAP_BASELINE_FILE
    exclude_patterns: tuple[str, ...] = DEFAULT_EXCLUDE_PATTERNS
