# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- **Em dash normalization** - Replaced all em dashes (-) with regular hyphens (-) in prose, configuration, and documentation for consistency and CI gate compliance.
- **Inline comment cleanup** - Removed unnecessary inline comments from core modules (cli.py, loc_cap.py) and core source files, preserving only `noqa` and `SENSITIVE` annotations.
- **Test coverage improvements** - Added comprehensive CLI invocation tests (11 subprocess-based tests and 6 direct main() entry point tests) to exercise real command-line usage patterns with temporary project fixtures. Coverage improved from 90% to 91% statement coverage, with cli.py reaching 96%.
- **Tag format clarification** - Updated exception tag documentation and examples to use consistent hyphen separators (e.g., 'facade - celery schedule' per hardened naming rules).

## [0.1.0] - 2026-07-10

### Added

- **Monorepo consolidation** - Consolidated strict-module 0.5.0 into the strict-suite monorepo. Package import root (`strict_module`) and CLI entry points (`strict-module`, `dto-strict`) remain unchanged.
- **R007 rule** - Pytest fixtures defined outside conftest.py are now flagged as violations.
- **R008 rule** - Bare module-level test functions (not in Test<Concern> classes) are now flagged as violations.
- **LOC cap subcommand** - `strict-module loc-cap` and `dto-strict loc-cap` enforce lines-of-code limits with configurable hard caps and soft targets.
- **Backward-compatible configuration** - Both `[tool.strict-module]` and legacy `[tool.dto-strict]` config sections are supported.

---

## Historical Changelog

For strict-module v0.1.0-v0.5.0 release history, see [CHANGELOG-history.md](docs/strict_module/CHANGELOG-history.md).
