# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.6.0] - 2026-10-18

### Added

- **"module-level:" default exception tag** - `# module-level: <reason>` is recognized out of the box, so a function that records why it is module-level is exempt from R009. The existing defaults (`facade - celery schedule`, `FRAMEWORK`) are unchanged.

### Changed

- **Baseline file validation is strict** - Previously, any error loading a baseline file (missing path, invalid JSON, missing entry keys) silently disabled the ratchet. Now all validation errors raise `BaselineLoadError` with a descriptive message to stderr. The ratchet only activates when a valid baseline is loaded.
- **R009 advisory by default** - R009 is INFO, so its findings print and never change the exit code. Decorated functions, dunder and `pytest_*` hooks, and functions tagged on the def line or in the first docstring line are exempt. Set `severity_overrides = { R009 = "HIGH" }` to restore the blocking behaviour.
- **R004 narrowed to the facade shape** - R004 flags only module-level functions in service paths whose body is a bare delegation to a class method (`Name.method(...)`, `Name(...).method(...)`, or an instance built and called on the next line). Untagged functions with real logic in service paths no longer fail; they are R009 advice. Wrappers that the old attribute-call test exempted (for example `return UserService.get_user(...)`) now fail unless tagged.
- **Exception tag default is the written form** - The default tag is `module-level:` (with the colon), not `module-level`. A docstring that merely mentions module-level as prose no longer exempts a function; only `# module-level: <reason>` on the def line or the first docstring line does.
- **Exception tag matching is shared** - R004 and R009 use one matcher: case-insensitive, read from the def line or the first docstring line. R004 previously matched case-sensitively and read the whole docstring.
- **loc-cap advisory text** - The hard-cap advisory no longer refers to a document that is not part of the public repository, and its refactor example uses a generic module name.
- **Unreadable input raises a typed error from the library API** - `DtoStrictLinter.lint_file` raises `LintInputError` for an unreadable or unparseable file (it previously returned an empty list). `LocCap.count_lines` raises `LocCapInputError` for an unreadable file (it previously returned 0), and `LocCap.load_baseline` raises it for an undecodable baseline (it previously returned an empty mapping). The CLI converts these into the stderr error and exit 1.
- **loc-cap success line is ASCII** - The success line that the LOC cap prints when every file is within the cap now starts with `OK:` instead of a check-mark glyph.
- **Linter internals** - The unused `violations` attribute of `DtoStrictLinter` is removed; no public name changed.

### Fixed

- **Baseline loading error handling** - `load_baseline()` now raises a typed `BaselineLoadError` for missing, unreadable, malformed, undecodable (non-UTF-8), or structurally invalid baseline files instead of silently returning an empty dict. Missing or malformed baselines are now hard errors that fail the gate with exit code 1, preventing silent ratchet disablement.
- **Malformed pyproject.toml exits with an error** - A file that cannot be read or parsed, or whose strict-module table is not a table, previously disabled all configuration silently. The CLI now prints the path and exits 1. A missing file still uses the defaults.
- **Annotation matching is by name** - R006 no longer flags identifiers that only contain the letters "any" (for example `Company`). R001 detects a qualified `typing.Any` inside `Dict[str, typing.Any]` and no longer matches names such as `AnyStr`.
- **R002 function context** - A dict literal after a function that carried an exception tag is no longer excused by that tag.
- **R011 constants modules** - Only a `constants.py` file, a `*_const.py` file, or a file under a directory named `constants` is exempt. A path that merely contains the word no longer is.
- **R003 on Python 3.14** - A dataclass keyword set to a bare name no longer raises on Python 3.14, which removed the legacy node class the rule referenced.
- **Unreadable or unparseable input fails the run** - A Python file the linter cannot decode or parse, or a file or baseline the LOC cap cannot decode, previously passed silently (the linter skipped the file and the LOC cap counted it as zero lines). The run now prints the path and the reason to stderr and exits 1. This includes `--generate-baseline`, which refuses to write a baseline from an unparseable file.
- **R007 duplicate reports** - A fixture function with more than one fixture decorator yields one violation instead of one per decorator.

### Removed

- **Unused path-pattern constant** - `DICT_STR_ANY_PATTERN` is removed from `strict_config.constants` (and from the `strict_config` package namespace). The package had no remaining reader for it.

## [0.5.0] - 2026-07-22

### Added

- **Four formatting dialect rules (R012-R015)** - New INFO-tier rules enforce formatting patterns for calls, signatures and try blocks:
  - **R012 (fits-one-line-stays)** - Flags single-argument calls under 80 chars split unnecessarily across lines. Enforces the fits-on-one-line principle.
  - **R013 (signature grouping)** - Flags multi-parameter method signatures (3-4+ params after self/cls) where each parameter is on its own line when grouping 2-3 per line would fit. Enforces compact method signatures.
  - **R014 (kwarg-call grouping)** - Flags multi-kwarg calls (2 kwargs) split across separate lines when they could be grouped. Enforces packed keyword groups. Findings report at the offending kwarg line; place `# noqa: R014` on the call line, not the kwarg line.
  - **R015 (wrap-path blank-line rhythm)** - Flags try/except blocks where statement count difference exceeds 3 statements, indicating asymmetric blank-line rhythm. Enforces wrap-path separation.

### Changed

- **INFO severity as non-blocking tier** - R012-R015 implemented at INFO severity; violations report but do not fail CI (exit code 0). Suppressible via `# noqa: R01X`. First release of formatting rules as advisory tier for one adoption cycle.
- **Canonical calibration** - All four rules validated against 29 reference files; zero violations on the canonical implementations. R014 flagged the expected findings in a five-file reference corpus (2, 4 and 7 findings in three of the files); R012, R013 and R015 reported zero violations on both the reference and re-aligned files.

## [0.4.0] - 2026-07-21

### Changed

- **Full-split wheel roots** - Restructured strict-suite from monolithic `strict_module` into 7 separate wheel roots (strict_checkers, strict_config, strict_inspection, strict_linter, strict_loc_cap, strict_rules) with acyclic dependency layering. Preserves git history via git mv; public API (strict_module shim) unchanged. Enables independent versioning and subset imports while maintaining backward compatibility.

## [0.3.1] - 2026-07-17

### Changed

- **Constants extraction** - Extracted hardcoded magic strings and configuration defaults to `strict_module/constants.py` for maintainability and consistency (severity levels, format types, exit codes, LOC cap defaults, config section names, noqa keywords, file patterns, exclude patterns). All 284 tests pass; coverage maintained at 95%.

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
