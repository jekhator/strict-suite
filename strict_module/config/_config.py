"""Configuration loading for strict-module (formerly dto-strict)."""

import sys
from typing import Self

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LocCapConfig:
    """Configuration for LOC cap checker."""

    hard_cap: int = 694
    soft_target: int = 500
    baseline_file: str = ".loc-cap-baseline.txt"


@dataclass(frozen=True, slots=True)
class Config:
    """Configuration for strict-module linter."""

    service_paths: list[str] = field(
        default_factory=lambda: ["apps/*/services/*.py", "**/services/*.py"]
    )
    dto_paths: list[str] = field(default_factory=lambda: ["**/dtos.py", "**/dtos/*.py"])
    exception_tags: list[str] = field(
        default_factory=lambda: ["facade - celery schedule", "FRAMEWORK"]
    )
    disabled_rules: list[str] = field(default_factory=list)
    severity_overrides: dict[str, str] = field(default_factory=dict)
    strict_collections: bool = field(default=False)
    exception_tag_requires_justification: bool = field(default=False)
    max_exception_tags_per_file: int | None = field(default=None)
    r003_mode: str = field(default="canonical")
    r006_paths: list[str] = field(
        default_factory=lambda: ["apps/*/services/*.py", "**/services/*.py"]
    )
    min_dict_keys: int = field(default=3)
    r003_strict_repr: bool = field(default=True)
    loc_cap: LocCapConfig = field(default_factory=LocCapConfig)

    @classmethod
    def from_pyproject(cls, path: Path) -> Self:
        """Load configuration from pyproject.toml."""
        if not path.exists():
            return cls()

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            return cls()

        tool_data = data.get("tool", {})
        config_data = tool_data.get("strict-module") or tool_data.get("dto-strict", {})
        loc_cap_data = config_data.get("loc-cap", {})

        loc_cap = LocCapConfig(
            hard_cap=loc_cap_data.get("hard_cap", 694),
            soft_target=loc_cap_data.get("soft_target", 500),
            baseline_file=loc_cap_data.get("baseline_file", ".loc-cap-baseline.txt"),
        )

        return cls(
            service_paths=config_data.get(
                "service_paths",
                ["apps/*/services/*.py", "**/services/*.py"],
            ),
            dto_paths=config_data.get("dto_paths", ["**/dtos.py", "**/dtos/*.py"]),
            exception_tags=config_data.get(
                "exception_tags",
                ["facade - celery schedule", "FRAMEWORK"],
            ),
            disabled_rules=config_data.get("disabled_rules", []),
            severity_overrides=config_data.get("severity_overrides", {}),
            strict_collections=config_data.get("strict_collections", False),
            exception_tag_requires_justification=config_data.get(
                "exception_tag_requires_justification", False
            ),
            max_exception_tags_per_file=config_data.get("max_exception_tags_per_file"),
            r003_mode=config_data.get("r003_mode", "canonical"),
            r006_paths=config_data.get(
                "r006_paths",
                ["apps/*/services/*.py", "**/services/*.py"],
            ),
            min_dict_keys=config_data.get("min_dict_keys", 3),
            r003_strict_repr=config_data.get("r003_strict_repr", True),
            loc_cap=loc_cap,
        )

    def is_rule_enabled(self, rule_id: str) -> bool:
        """Check if a rule is enabled."""
        return rule_id not in self.disabled_rules
