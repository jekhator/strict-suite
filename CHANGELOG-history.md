# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

### Changed

### Fixed

## [0.5.0] - 2026-07-06

### Changed

- **Package renamed from `dto-strict` to `strict-module`** - Renamed to follow category-first naming conventions (strict- prefix). GitHub repository renamed to `github.com/jekhator/strict-module`. PyPI package name updated to `strict-module`.
- **Flattened package layout** - Source code moved from `src/dto_strict/` to `strict_module/` at repository root, adopting the suite's standard flat-namespace layout.
- **Version single-sourced in `strict_module/config/_version.py`** - Eliminates version drift between package metadata and source. Hatch now dynamically reads version from this file.

### Added

- **Backward-compatible config fallbacks** - Configuration loading now checks `[tool.strict-module]` first, then falls back to `[tool.dto-strict]` for compatibility with existing codebases. Both are supported; new code should use `[tool.strict-module]`.
- **Backward-compatible baseline fallbacks** - Baseline file loading checks `.strict-module-baseline.json` first, then falls back to `.dto-strict-baseline.json`.
- **Entry point alias** - The `dto-strict` CLI command remains available as a backward-compatibility alias, pointing to the same implementation as the new `strict-module` command.
- **Comprehensive compatibility tests** - New test suite (`test_compat_fallback.py`) covers config and baseline file fallback scenarios.

### Deprecated

- `[tool.dto-strict]` configuration section - use `[tool.strict-module]` instead. Old section still works but will be removed in v1.0.
- `dto-strict` CLI command name - use `strict-module` instead. Old name still works but will be removed in v1.0.
- `.dto-strict-baseline.json` filename - use `.strict-module-baseline.json` instead. Old filename still works but will be removed in v1.0.

## [0.4.1] - 2026-06-11

### Fixed

- **R002 no longer false-positives on dict literals returned from to_* serializer methods** - Dict literals returned from methods whose name starts with `to_` in a `@dataclass`-decorated class are now correctly exempted. The returned dict is the dataclass's serialized output, not an unconverted business shape. Non-dataclass classes and non-`to_*` methods remain flagged as before. Example: `class UserDTO` with `def to_dict(self) -> dict: return {"id": self.id, "name": self.name, "email": self.email}` now passes (no R002 violation).

- **`dto-strict loc-cap` now exempts test files from the line-of-code cap** - Test files are automatically excluded from LOC enforcement, mirroring the v0.4.0 lint exemption set. A file is a test file if its basename is `conftest.py`, matches `test_*.py`, or is under a `tests/` directory. This prevents test fixtures and test helpers from inflating LOC metrics. Baseline files remain unaffected; improvements in test files are still reflected in ratchet calculations.

### Changed

- `is_test_file()` utility now checks for `/tests/` directory path segments in addition to basename patterns. This enables `loc-cap` to properly exempt test files found anywhere under a `tests/` directory structure.

## [0.4.0] - 2026-06-07

### Added

- **Test file exemption from DTO rules (R001, R004, R006)** - Service-layer rules (R001, R004, R006) now automatically exempt test files from linting. A file is considered a test file if its basename is `conftest.py`, matches `test_*.py`, or contains a `/tests/` path segment. This prevents false positives in test fixtures and test helpers that may use `Dict[str, Any]`, module-level functions, or `typing.Any` for legitimate testing purposes.

- **R007 - Pytest fixtures must be in conftest.py** - New rule that flags `@pytest.fixture` decorators defined in test files other than `conftest.py`. Fixtures are test infrastructure and belong in the module-level fixtures file (conftest.py), not scattered across test modules. Rule applies only to test files (basename `conftest.py`, `test_*.py`, or under `/tests/`).

- **R008 - Bare module-level test functions** - New rule that flags test functions (matching `def test_*`) defined at module level in test files. Test functions must be organized into `Test<Concern>` classes for clarity and pytest discovery. Rule applies only to test files.

### Changed

- `is_service_path()` and `is_dto_path()` now check `is_test_file()` before pattern matching, ensuring test files never match service or DTO paths regardless of naming.

### Improved

- Configuration section for pytest discipline rules now documented in README (new "Pytest Discipline" section).

## [0.3.0] - 2026-06-04

### Added

- **`dto-strict loc-cap` subcommand - per-file LOC-cap ratchet enforcer** - New CLI subcommand for enforcing line-of-code limits on Python files with configurable hard/soft caps and baseline-driven ratcheting. Ported from the per-repo `check_loc_cap.py` pattern into dto-strict's unified command surface.
  - **Hard cap** (default: 694 LOC) - fails the check if any file exceeds this limit (NEW offenders fail immediately; baselined files that grew also fail).
  - **Soft target** (default: 500 LOC) - warnings for files exceeding soft target but under hard cap (suggest decomposition).
  - **Ratchet baseline** (via `--baseline .loc-cap-baseline.txt` or config `[tool.dto-strict.loc-cap].baseline_file`) - baselined files cannot exceed their recorded LOC; improvements are allowed.
  - **Generate baseline** (via `--generate-baseline`) - outputs baseline in `path:loc` format (sorted by LOC descending) for capture into version control.
  - CLI flags: `--hard-cap`, `--soft-target`, `--baseline`, `--generate-baseline`, `--config` (pyproject.toml path).
  - Pyproject config section: `[tool.dto-strict.loc-cap]` with keys `hard_cap`, `soft_target`, `baseline_file` (CLI flags take precedence).
  - Exclusion patterns: `migrations`, `management/commands` (hardcoded, Django-scoped).
  - Exit code: 0 for pass (soft warnings allowed), 1 for hard violations.

### Changed

- **CLI now dispatches on subcommand**: `sys.argv[1] == "loc-cap"` routes to `handle_loc_cap()` before standard argparse. Bare `dto-strict <path>` DTO-discipline lint is unchanged (backcompat preserved).
- **Added tomli backport dependency** for Python 3.10 (tomllib native in 3.11+), enabling pyproject.toml parsing for loc-cap config in both Python versions.

### Improved

- Configuration now loads `[tool.dto-strict.loc-cap]` section from pyproject.toml alongside existing `[tool.dto-strict]` linter options.
## [0.2.2] - 2026-05-22

### Fixed

- **R002 no longer false-positives on annotated module-level / class-level constants** - Typed static data declarations like `DISPLAY_LABELS: dict[str, str] = {...}` are now correctly skipped. The explicit type annotation signals intent ("this is typed static data") distinct from R002's actual target ("inline dict literal as business shape in service code"). Now R002 skips:
  - `ast.AnnAssign` at module scope (module-level typed constants)
  - `ast.AnnAssign` inside class body (class-level typed constants)
  
  Still flags:
  - `ast.Assign` without annotation at module scope (ambiguous intent)
  - Inline dict literals inside function bodies (original intent)
  Regression tests added in `tests/test_r002_annotated_constants.py`.

- **Noqa suppression now correctly handles em-dashes and multi-line dicts** : v0.2.1's `has_noqa_comment` was broken for explanations using em-dashes (-) instead of hyphens (-). The function only stripped trailing hyphens (`-`), causing specs like `"dto-strict-R002 - explanation"` to remain unmatched. Now handles all dash variants: hyphen, en-dash, and em-dash characters. Additionally clarified that multi-line dict noqa comments must be on the opening brace line (ast node's `lineno`). Test suite `tests/test_noqa_r002.py` covers 7 scenarios: trailing-hyphen, trailing-emdash, opening-brace, no-noqa, wrong-rule, bare-noqa, and before-line (should NOT suppress).


## [0.2.1] - 2026-05-21

### Fixed

- **`has_noqa_comment` is now implemented** - Previously a stub returning False, suppression via `# noqa: dto-strict-RXXX` comments was silently broken. Now properly parses and recognizes:
  - `# noqa` (suppresses all rules)
  - `# noqa: dto-strict` (suppresses all dto-strict rules)
  - `# noqa: dto-strict-R001` (suppresses specific rule)
  - `# noqa: dto-strict-R001, dto-strict-R002` (suppresses multiple rules)
  All checkers now honor suppression comments.

### Documentation

- **Clarified R003 canonical-pivot wording** - Description now explicitly states "Flag `repr=False` in dataclasses (v0.2 canonical: plain `@dataclass(frozen=True, slots=True)` without `repr=False`)", making the v0.2 shift from v0.1 explicit.
- **Added "PHI / Sensitive Data Handling (Pattern 1)" section** - Explains the intentional move from blanket `repr=False` to explicit `__repr__` overrides on sensitive DTOs. Includes healthcare/HIPAA context and example code for masking PII fields.
- **Added "Suppressing Violations" section** - Documents the now-functional `# noqa: dto-strict-RXXX` syntax with practical examples.
- **Mentioned healthcare/HIPAA use case in "Why dto-strict?"** - Added context on why DTO discipline is critical in regulated healthcare systems managing patient records and compliance documents.

## [0.2.0] - 2026-05-13

### Added

- **Issue #1 - R004 auto-detect class-method-wrapping pattern**: R004 now auto-detects when module-level functions delegate to class methods, reducing false positives. Functions that exclusively wrap class methods (e.g., `return _service.method(...)` or `return ClassName.method(...)`) no longer require exception tags. Exception tags still work as override.

- **Issue #2 - R002 configurable min_dict_keys threshold**: R002 now supports a configurable `min_dict_keys` setting (default: 3). This allows teams to enforce stricter or looser inline dict literal thresholds. Configure in `pyproject.toml`:
  ```toml
  [tool.dto-strict]
  min_dict_keys = 2  # Flag dicts with 2+ keys instead of 3+
  ```

- **Issue #3 - R003 strict/relaxed modes for frozen+slots+repr=False trio**: R003 now supports `r003_strict_repr` mode (default: true in canonical mode).
  - **Strict mode** (default): `repr=False` is flagged as anti-canonical. Canonical pattern is `@dataclass(frozen=True, slots=True)` WITHOUT `repr=False`.
  - **Relaxed mode**: Only checks for `frozen=True, slots=True`; ignores `repr=False` (useful for gradual migrations). Configure:
    ```toml
    [tool.dto-strict]
    r003_strict_repr = false  # Enable relaxed mode
    ```

- **Issue #4 - Baseline ratchet-from-baseline mode**: New `--generate-baseline` and `--baseline` CLI flags enable "technical debt ratcheting":
  - `dto-strict apps/ --generate-baseline > .dto-strict-baseline.json` - Capture current violations as accepted debt.
  - `dto-strict apps/ --baseline .dto-strict-baseline.json` - Subsequent runs accept baseline violations; new violations trigger failure (exit 1).
  - Baseline entries are hashed by file + line + rule_id for stability against message wording changes.

### Changed

- R003 canonical mode now defaults to `r003_strict_repr=true`, treating `repr=False` as anti-canonical and flagging it for removal.
- CLI argument `path` now optional when using `--generate-baseline` (path is required for normal linting).

### Improved

- Configuration loading now supports `min_dict_keys` and `r003_strict_repr` options in `[tool.dto-strict]` section of `pyproject.toml`.

### Bug Fixes

- None in v0.2.0.

## [0.1.0] - Earlier Versions

See git history for prior releases.
