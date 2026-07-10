# Config Layer - Security Audit

**Date:** 2026-07-09
**Component:** strict_module/config/_config.py
**Scope:** Configuration file parsing, defaults, and initialization

## Security Assessment

The config layer loads settings from pyproject.toml files and provides sensible defaults. This audit evaluates configuration parsing safety and data handling.

### TOML File Parsing

Python 3.11+ uses stdlib tomllib; Python 3.10 falls back to tomli package. Files are opened in binary mode ("rb") and parsed via tomllib.load(f).

Security considerations:
- TOML parsing is handled by a trusted library (stdlib or tomli).
- File I/O catches all exceptions; missing or malformed files return default config.
- TOML syntax is declarative; no code execution during parsing.

No TOML injection or code execution risks.

### Config Data Access

Config data is extracted via dict.get() with sensible defaults. Nested access (tool -> strict-module or tool -> dto-strict) safely handles missing keys.

Security considerations:
- Type conversions (int, str, bool) are explicit; invalid values raise exceptions caught and handled.
- Backward compatibility: Supports both "strict-module" and "dto-strict" section names.
- LocCapConfig is extracted from [tool.strict-module.loc-cap] or returns a default.

Safe and defensive.

### Immutability

Config and LocCapConfig use @dataclass(frozen=True, slots=True). Once initialized, configs cannot be modified; this prevents mutation attacks after construction.

Security observation: Frozen dataclasses prevent accidental or malicious modification of configuration settings.

### Defaults

Hardcoded defaults are sensible:
- service_paths: Standard Django service layer patterns
- exception_tags: Common tags ("facade", "FRAMEWORK")
- LOC cap hard cap: 694 (historical reference baseline)
- LOC cap soft target: 500

Assessment: Defaults are conservative and reasonable for typical projects.

### Version Compatibility

Config supports both Python 3.11+ (tomllib) and Python 3.10 (tomli). Version check uses sys.version_info.

Assessment: Compatibility check is explicit and correct.

## Conclusion

TOML parsing is safe. Config access is defensive and handles missing files gracefully. Frozen dataclasses prevent modification. Defaults are conservative.

No security vulnerabilities identified in config layer.
