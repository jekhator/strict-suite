"""AST-based linter for Python DTO discipline and facade-ban enforcement."""

from strict_config import __version__
from strict_linter import DtoStrictLinter, Rule, RuleSeverity

__all__ = ["DtoStrictLinter", "Rule", "RuleSeverity", "__version__"]
