"""AST-based linter for Python DTO discipline and facade-ban enforcement."""

from .config import __version__
from .linter import DtoStrictLinter
from .rules import Rule, RuleSeverity

__all__ = ["DtoStrictLinter", "Rule", "RuleSeverity", "__version__"]
