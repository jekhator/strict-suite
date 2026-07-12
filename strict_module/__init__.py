"""AST-based linter for Python DTO discipline and facade-ban enforcement."""

from strict_module.config import __version__
from strict_module.linter import DtoStrictLinter
from strict_module.rules import Rule, RuleSeverity

__all__ = ["DtoStrictLinter", "Rule", "RuleSeverity", "__version__"]
