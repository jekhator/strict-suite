"""Rule object definitions and violations."""

from dataclasses import dataclass
from enum import Enum

from strict_config.constants import (
    GITHUB_LEVEL_ERROR,
    GITHUB_LEVEL_NOTICE,
    GITHUB_LEVEL_WARNING,
)


class RuleSeverity(Enum):
    """Severity levels for violations."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


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
        if self.severity == RuleSeverity.HIGH:
            level = GITHUB_LEVEL_ERROR
        elif self.severity == RuleSeverity.INFO:
            level = GITHUB_LEVEL_NOTICE
        else:
            level = GITHUB_LEVEL_WARNING
        return f"::{level} file={self.file},line={self.line},col={self.col}::{self.message}"


@dataclass(frozen=True, slots=True)
class Rule:
    """Rule definition."""

    id: str
    name: str
    severity: RuleSeverity
    description: str
