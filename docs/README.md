# strict-suite Documentation

This directory contains documentation for the strict-suite linting and static analysis tools.

## Rules Reference

The linter ships 15 rules. The severity shown is the default. `severity_overrides` changes the severity of one rule, and `disabled_rules` turns a rule off.

| Rule ID | Name | Severity | Description |
|---------|------|----------|-------------|
| R001 | Dict[str, Any] or bare collections in signatures | HIGH | Service-layer function signatures must not use `Dict[str, Any]`, or bare `dict`, `list`, `tuple` when `strict_collections` is enabled |
| R002 | Inline dict literals (3+ keys) | MEDIUM | Large inline dict literals in service code should be converted to DTOs instead; exception tags can require justification |
| R003 | repr=False on dataclass | MEDIUM | Dataclasses should use canonical `@dataclass(frozen=True, slots=True)` without `repr=False` |
| R004 | Facade: module-level wrapper around a class method | HIGH | A module-level function in a service path whose body only delegates to a class method must be called directly, or carry an exception tag |
| R005 | Validator pattern | LOW | Validator functions should use the `DTO.from_dict()` pattern for type coercion |
| R006 | typing.Any in signatures | HIGH | Functions must not use `typing.Any` in parameters or return types |
| R007 | Pytest fixture outside conftest | MEDIUM | Pytest fixtures must be defined in conftest.py, not scattered across test files |
| R008 | Bare module-level test function | MEDIUM | Test functions must be methods in `Test<Concern>` classes, not module-level functions |
| R009 | Module-level function without a recorded reason | INFO | A method on a class is the default shape; advisory, see below |
| R010 | Legacy typing aliases for ABCs | MEDIUM | ABC imports must come from `collections.abc`, not `typing` |
| R011 | String literal at raise site | HIGH | Raise statements must reference `ERR_*` constants, not inline string literals or f-strings |
| R012 | Call fits on one line but is exploded | INFO | A multi-line call with one argument that fits on one line should be collapsed |
| R013 | Signature grouping (compact method signatures) | INFO | Handler methods (names starting with `log_`, `record_` or `wrap_`) should group 2-5 parameters per line |
| R014 | Kwarg-call grouping (packed keyword groups) | INFO | Log-event calls should pack 2-3 kwargs per line |
| R015 | Wrap-path blank-line rhythm | INFO | An except block's blank-line rhythm should mirror its try block |

INFO findings print and never change the exit code. HIGH, MEDIUM and LOW findings each set their own non-zero exit code.

## Module-Level Functions (R004 and R009)

A method on a class is the default shape. A module-level function is acceptable when it is the optimal shape: a framework registration point that requires a function (task, view, signal receiver, command, fixture, hook), a program entry point, a protocol-required module hook, or a small stateless helper with no natural owning class. Record the choice on the def line with `# module-level: <reason>`. A facade (a module-level function that only delegates to a class method, adding no logic of its own) is not an acceptable shape.

- **R009** (INFO, every non-test file) reports module-level functions without a recorded reason. It is advisory and never changes the exit code. These are exempt: the `main` and `handle_*` entry points, decorated functions, dunder module hooks (for example `__getattr__` and `__dir__`), `pytest_*` hook functions, functions with an exception tag on the def line or in the first line of the docstring, and `# noqa: R009`.
- **R004** (HIGH, service paths) reports facades. The body, after an optional docstring, is a single delegation to a class method with no logic of its own. The recognized shapes are `return Name.method(...)`, `return Name(...).method(...)`, `return Name().method(...)`, and `instance = Name(...)` followed by `return instance.method(...)`, where `Name` starts with a capital letter. A bare `Name.method(...)` expression statement counts too. Any other module-level function in a service path is R009's business.

To restore the former blocking behaviour of R009, set its severity to HIGH in `pyproject.toml`:

```toml
[tool.strict-module]
severity_overrides = { R009 = "HIGH" }
```

Exception tags are plain substrings matched case-insensitively. The defaults are `facade - celery schedule`, `FRAMEWORK` and `module-level:`. The colon form is deliberate: `module-level` without the colon would also match prose in a docstring, so only the written form `# module-level: <reason>` exempts a function. A project can add its own, for example `aws-boundary`, in `exception_tags`; setting that key replaces the defaults.

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

These audit and review documents describe the package layout at the time they were written (before the split into the strict_* root packages in 0.4.0), so their module paths are historical.

### Historical Documentation

- `CHANGELOG-history.md`: Release history for strict-module v0.1.0-v0.5.0 (consolidated into this project as v0.1.0)

## Components

### CLI (`strict_module/cli.py`)

The command-line interface provides two equivalent entry points:
- `strict-module`: Primary CLI entry point
- `dto-strict`: Backward-compatible alias

**Main subcommands:**
- Default (file/directory path): Run the linting rules R001-R015
- `loc-cap`: Check lines-of-code limits with configurable hard/soft caps

**Output formats:**
- `text` (default): Plain text, one violation per line
- `github`: GitHub Actions annotation format
- `json`: Machine-readable JSON format

### Configuration Layer (`strict_config/_config.py`)

Configuration is loaded from `pyproject.toml` with the following sections:

**Section name:** `[tool.strict-module]` (also supports legacy `[tool.dto-strict]` for backward compatibility)

**Options:**
- `service_paths`: Glob patterns for files to lint with strict rules (e.g., `["**/services/*.py"]`)
- `dto_paths`: Glob patterns for files expected to contain DTOs (e.g., `["**/dtos.py"]`)
- `exception_tags`: Recognized justification tags for module-level functions (R004 and R009) and dict literals (R002), e.g. `aws-boundary`
- `disabled_rules`: List of rule IDs to disable globally (e.g., `["R005"]`)
- `severity_overrides`: Dict mapping rule IDs to override severity levels (e.g., `{"R002": "HIGH", "R011": "INFO"}`)
- `loc_cap`: LOC cap configuration (hard_cap, soft_target, baseline_file)

### Linter and Rules Engine (`strict_linter/linter_client.py`, `strict_rules/rules_client.py`)

The core AST-based analysis engine that detects violations:

1. Parses Python files into AST
2. Walks the tree with one checker per rule (`strict_checkers/`), checking R001-R015
3. Filters violations based on:
   - Disabled rules and severity overrides
   - Baseline ratchet file (accepted violations)
4. Returns violations with line/column info and formatted messages

**Rule application scope:**
- R001, R002, R004, R006: Service-layer files (matched against `service_paths`; R006 uses `r006_paths`)
- R003: DTO files (matched against `dto_paths`)
- R005, R010, R012-R015: All files
- R007, R008: Test files only (R007 checks pytest fixtures outside conftest.py; R008 checks module-level test functions)
- R009: Every non-test file
- R011: Every non-test file except constants modules

### LOC Cap Subcommand (`strict_loc_cap/loc_cap_client.py`)

Enforces lines-of-code limits per file:

- **Hard cap**: Absolute limit; violations FAIL the check (default 694 lines)
- **Soft target**: Guideline; violations warn but don't fail (default 500 lines)
- **Baseline ratchet**: Baseline file (`.loc-cap-baseline.txt`) tracks accepted overages; prevents new violations
- **Generate mode**: Generates baseline from current state (output to stdout)

Test files are excluded from LOC cap checks.

## Suppression via noqa Comments

Violations can be suppressed inline using `# noqa` comments:

- **Bare suppression:** `# noqa` suppresses any rule on that line.
- **Rule-specific:** `# noqa: R006` suppresses rule R006 only.
- **Multiple rules:** `# noqa: R006, R011` suppresses both R006 and R011.
- **Namespaced form:** `# noqa: strict-module-R006` is accepted by strict-module. Ruff 0.15.14 reports an invalid `# noqa` directive for this form.

**Ruff coexistence:** Ruff 0.15.14 warns about the namespaced form, and the `external` setting does not change that. When ruff checks the same file, use the bare rule code (`# noqa: R006`).

## Backward Compatibility

As of v0.1.0, strict-suite consolidates the strict-module v0.5.0 package. The following are preserved:

- **Config section names:** Both `[tool.strict-module]` and legacy `[tool.dto-strict]` are recognized
- **Baseline files:** Any path can be passed to `--baseline`; the LOC cap baseline also falls back to the legacy names `.strict-module-baseline.txt` and `.dto-strict-baseline.txt`
- **CLI entry points:** Both `strict-module` and `dto-strict` commands work identically

## Development

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines, development setup, and testing procedures.
