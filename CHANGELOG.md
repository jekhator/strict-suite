# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.3.0] - 2026-07-17

### Fixed

- **Severity overrides now apply correctly** - The `severity_overrides` config now actually applies severity changes to violations (was previously building overridden violations but not returning them).
- **Noqa rule-code shorthand** - Support bare rule code syntax in noqa comments (e.g., `# noqa: R006` in addition to `# noqa: strict-module-R006`); enables ruff-standard idioms.

### Added

- **INFO severity level** - New `RuleSeverity.INFO` allows non-blocking violations (exit code 0 even when violations present); `severity_overrides = {"R011": "INFO"}` prints violations but does not fail the lint check.

## [0.2.0] - 2026-07-14

### Added

- **R009 rule** - Module-level functions outside entry points are now flagged as violations (enforces container-based service-class pattern).
- **R010 rule** - Legacy typing ABC imports (Callable, Mapping, Iterable, etc.) are now flagged; use collections.abc instead.
- **R011 rule** - String literals at raise sites are flagged; use named constants instead for maintainability.

### Changed

- **Config parity with domain-suite** - Added `paths` configuration and `[tool.strict-module.loc-cap]` section to pyproject.toml for consistency; renamed workflow from stricts.yml to strict-module.yml.
- **Standard ruff rule-set parity** - Enabled I (isort), TID252 (relative imports), PLC0414 (unused imports), and UP035 (deprecated typing) ruff rules; all conform to OSS suite standards.
- **Coverage gate to 95%** - Raised pytest coverage gate from 94% to 95% via `--cov-fail-under=95`; achieved 95.05% statement coverage with targeted test expansion across all checker modules (linter.py 99%, rules.py 94%, cli.py 96%).
- **Conformance doc conventions** - Created docs/conformance-audit.md documenting full-corpus audit of strict_module against R001-R010 rules; all violations resolved.
- **Python 3.11+ and tomllib cleanup** - Removed Python 3.10 compatibility layer (conditional tomli dependency); requires-python floor now >=3.11 only. Simplified config-loading imports to use native tomllib.
- **Em dash and inline-comment cleanup** - Replaced em dashes with hyphens in docs; removed unnecessary inline comments, preserving only noqa and SENSITIVE annotations.

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
