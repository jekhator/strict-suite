"""Configuration loading for strict-module (formerly dto-strict)."""

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from strict_config.constants import (
    CONFIG_SECTION_DTO_STRICT,
    CONFIG_SECTION_LOC_CAP,
    CONFIG_SECTION_STRICT_MODULE,
    DEFAULT_DTO_PATHS,
    DEFAULT_EXCEPTION_TAGS,
    DEFAULT_LOC_CAP_BASELINE_FILE,
    DEFAULT_LOC_HARD_CAP,
    DEFAULT_LOC_SOFT_TARGET,
    DEFAULT_MIN_DICT_KEYS,
    DEFAULT_R003_MODE,
    DEFAULT_R006_PATHS,
    DEFAULT_SERVICE_PATHS,
)


@dataclass(frozen=True, slots=True)
class LocCapConfig:
    """Configuration for LOC cap checker."""

    hard_cap: int = DEFAULT_LOC_HARD_CAP
    soft_target: int = DEFAULT_LOC_SOFT_TARGET
    baseline_file: str = DEFAULT_LOC_CAP_BASELINE_FILE


@dataclass(frozen=True, slots=True)
class Config:
    """Configuration for strict-module linter."""

    service_paths: list[str] = field(
        default_factory=lambda: DEFAULT_SERVICE_PATHS.copy()
    )
    dto_paths: list[str] = field(default_factory=lambda: DEFAULT_DTO_PATHS.copy())
    exception_tags: list[str] = field(
        default_factory=lambda: DEFAULT_EXCEPTION_TAGS.copy()
    )
    disabled_rules: list[str] = field(default_factory=list)
    severity_overrides: dict[str, str] = field(default_factory=dict)
    strict_collections: bool = field(default=False)
    exception_tag_requires_justification: bool = field(default=False)
    max_exception_tags_per_file: int | None = field(default=None)
    r003_mode: str = field(default=DEFAULT_R003_MODE)
    r006_paths: list[str] = field(default_factory=lambda: DEFAULT_R006_PATHS.copy())
    min_dict_keys: int = field(default=DEFAULT_MIN_DICT_KEYS)
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
        config_data = tool_data.get(CONFIG_SECTION_STRICT_MODULE) or tool_data.get(
            CONFIG_SECTION_DTO_STRICT, {}
        )
        loc_cap_data = config_data.get(CONFIG_SECTION_LOC_CAP, {})

        loc_cap = LocCapConfig(
            hard_cap=loc_cap_data.get("hard_cap", DEFAULT_LOC_HARD_CAP),
            soft_target=loc_cap_data.get("soft_target", DEFAULT_LOC_SOFT_TARGET),
            baseline_file=loc_cap_data.get(
                "baseline_file", DEFAULT_LOC_CAP_BASELINE_FILE
            ),
        )

        return cls(
            service_paths=config_data.get("service_paths", DEFAULT_SERVICE_PATHS),
            dto_paths=config_data.get("dto_paths", DEFAULT_DTO_PATHS),
            exception_tags=config_data.get("exception_tags", DEFAULT_EXCEPTION_TAGS),
            disabled_rules=config_data.get("disabled_rules", []),
            severity_overrides=config_data.get("severity_overrides", {}),
            strict_collections=config_data.get("strict_collections", False),
            exception_tag_requires_justification=config_data.get(
                "exception_tag_requires_justification", False
            ),
            max_exception_tags_per_file=config_data.get("max_exception_tags_per_file"),
            r003_mode=config_data.get("r003_mode", DEFAULT_R003_MODE),
            r006_paths=config_data.get("r006_paths", DEFAULT_R006_PATHS),
            min_dict_keys=config_data.get("min_dict_keys", DEFAULT_MIN_DICT_KEYS),
            r003_strict_repr=config_data.get("r003_strict_repr", True),
            loc_cap=loc_cap,
        )

    def is_rule_enabled(self, rule_id: str) -> bool:
        """Check if a rule is enabled."""
        return rule_id not in self.disabled_rules
