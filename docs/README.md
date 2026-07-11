# strict-suite Documentation

This directory contains comprehensive documentation for the strict-suite linting and static analysis tools.

## Rules Reference

The linter enforces 8 rules across Python code:

| Rule ID | Name | Severity | Description |
|---------|------|----------|-------------|
| R001 | Dict[str, Any] in signatures | HIGH | Function signatures must not use bare `dict`, `list`, `tuple`, or `Dict[str, Any]` in service code |
| R002 | Inline dict literals (3+ keys) | MEDIUM | Large inline dict literals should be converted to DTOs instead |
| R003 | repr=False on dataclass | MEDIUM | Dataclasses should use canonical `@dataclass(frozen=True, slots=True)` without repr=False |
| R004 | Module-level function without tag | HIGH | Module-level functions must have documented exception tags (e.g., `# facade: celery schedule`) |
| R005 | Validator pattern | LOW | Validator functions should use `DTO.from_dict()` pattern for type coercion |
| R006 | typing.Any in signatures | HIGH | Functions must not use `typing.Any` in parameters or return types |
| R007 | Pytest fixture outside conftest | MEDIUM | Pytest fixtures must be defined in conftest.py, not scattered across test files |
| R008 | Bare module-level test function | MEDIUM | Test functions must be methods in `Test<Concern>` classes, not module-level functions |

## Documentation Structure

### Audits and Reviews

- `audits/`: Security and design audits for each component
  - `cli-audit.md`: CLI module security audit
  - `config-layer-audit.md`: Configuration layer audit
  - `linter-rules-engine-audit.md`: Rules engine audit
  - `loc-cap-subcommand-audit.md`: LOC cap subcommand audit

- `reviews/`: Code review reports for each component
  - `cli-review.md`: CLI module review
  - `config-layer-review.md`: Configuration layer review
  - `linter-rules-engine-review.md`: Rules engine review
  - `loc-cap-subcommand-review.md`: LOC cap subcommand review

### Historical Documentation

- `CHANGELOG-history.md`: Release history for strict-module v0.1.0-v0.5.0 (consolidated into this project as v0.1.0)

## Components

### CLI (`strict_module/cli.py`)

The command-line interface provides two equivalent entry points:
- `strict-module`: Primary CLI entry point
- `dto-strict`: Backward-compatible alias

**Main subcommands:**
- Default (file/directory path): Run linting rules R001-R008
- `loc-cap`: Check lines-of-code limits with configurable hard/soft caps

**Output formats:**
- `text` (default): Plain text, one violation per line
- `github`: GitHub Actions annotation format
- `json`: Machine-readable JSON format

### Configuration Layer (`strict_module/config/`)

Configuration is loaded from `pyproject.toml` with the following sections:

**Section name:** `[tool.strict-module]` (also supports legacy `[tool.dto-strict]` for backward compatibility)

**Options:**
- `service_paths`: Glob patterns for files to lint with strict rules (e.g., `["**/services/*.py"]`)
- `dto_paths`: Glob patterns for files expected to contain DTOs (e.g., `["**/dtos.py"]`)
- `exception_tags`: Recognized justification tags for module-level functions (R004 exceptions)
- `disabled_rules`: List of rule IDs to disable globally (e.g., `["R005"]`)
- `severity_overrides`: Dict mapping rule IDs to override severity levels
- `loc_cap`: LOC cap configuration (hard_cap, soft_target, baseline_file)

### Linter Rules Engine (`strict_module/linter.py`, `strict_module/rules.py`)

The core AST-based analysis engine that detects violations:

1. Parses Python files into AST
2. Walks the tree checking for violations against R001-R008
3. Filters violations based on:
   - File path matching (service_paths, dto_paths, test files)
   - Disabled rules and severity overrides
   - Baseline ratchet file (accepted violations)
4. Returns violations with line/column info and formatted messages

**Rule application scope:**
- R001, R006: Service-layer functions (matched against `service_paths`)
- R002-R005: All files (configurable)
- R007: Test files only (R007 checks pytest fixtures)
- R008: Test files only (R008 checks test functions)

### LOC Cap Subcommand (`strict_module/loc_cap.py`)

Enforces lines-of-code limits per file:

- **Hard cap**: Absolute limit; violations FAIL the check (default 694 lines)
- **Soft target**: Guideline; violations warn but don't fail (default 500 lines)
- **Baseline ratchet**: Baseline file (`.loc-cap-baseline.txt`) tracks accepted overages; prevents new violations
- **Generate mode**: Generates baseline from current state (output to stdout)

Test files are excluded from LOC cap checks.

## Backward Compatibility

As of v0.1.0, strict-suite consolidates the strict-module v0.5.0 package. The following are preserved:

- **Config section names:** Both `[tool.strict-module]` and legacy `[tool.dto-strict]` are recognized
- **Baseline files:** Both `.strict-module-baseline.json` and legacy `.dto-strict-baseline.json` are supported
- **CLI entry points:** Both `strict-module` and `dto-strict` commands work identically

## Development

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines, development setup, and testing procedures.
