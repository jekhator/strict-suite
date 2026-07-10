# Config Layer - Code Review

**Date:** 2026-07-09
**Component:** strict_module/config/_config.py
**Focus:** Design, parsing, and defaults

## Architecture

Two dataclasses manage configuration:
1. LocCapConfig: LOC cap enforcement settings (hard_cap, soft_target, baseline_file)
2. Config: Global settings (service_paths, exception_tags, rule enablement, LOC cap config)

Both use @dataclass(frozen=True, slots=True) for immutability and memory efficiency.

Assessment: Frozen dataclasses enforce immutability; slots reduce memory footprint.

## Parsing Logic

Config.from_pyproject() loads from pyproject.toml at an arbitrary path:
1. Opens file in binary mode via tomllib.load() (or tomli for Python 3.10)
2. Extracts tool.strict-module (or tool.dto-strict for backward compat)
3. Builds Config and LocCapConfig instances from parsed data

Strengths:
- Path argument is flexible; not hardcoded to a location.
- Backward compatibility with "dto-strict" section name.
- Exception handling returns default Config if parsing fails.

Assessment: Implementation is robust and handles missing files gracefully.

## Defaults

LocCapConfig defaults:
- hard_cap: 694 (historical baseline)
- soft_target: 500 (conservative target)
- baseline_file: .loc-cap-baseline.txt

Config defaults:
- service_paths: ["apps/*/services/*.py", "**/services/*.py"]
- exception_tags: ["facade", "FRAMEWORK"]
- disabled_rules: [] (all enabled by default)
- r003_mode: "canonical" (strict dataclass enforcement)

Assessment: Defaults are conservative and suitable for most projects.

## Type System

Config and LocCapConfig fields use type hints: int, str, bool, list, dict, tuples. None union types are used where applicable (max_exception_tags_per_file: int | None).

Assessment: Type hints are comprehensive and enable static checking.

## Version Compatibility

Python version check uses sys.version_info >= (3, 11) to select tomllib vs tomli.

Strength: Explicit version check; no try-except import guessing.

Assessment: Compatibility is correct.

## Field Customization

Config supports extensive customization:
- Rule disabling: disabled_rules list
- Severity overrides: severity_overrides dict
- Custom service paths: service_paths list
- Strict collections: strict_collections bool
- R003 mode (canonical vs legacy): r003_mode string

Assessment: Customization options provide flexibility for diverse projects.

## Conclusion

The config layer is well-designed. Parsing is robust and handles missing files. Defaults are conservative. Immutability via frozen dataclasses is sound. Backward compatibility is thoughtful.

No significant code quality issues identified.
