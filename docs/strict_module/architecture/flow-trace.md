# strict_module Flow-Trace Diagram

strict_module is a CLI linter (not a decorator) that enforces DTO and facade discipline through AST analysis. It runs in two modes: standard linting (the default) and the `loc-cap` subcommand. This document traces the code paths as shipped in 0.6.0. File paths are relative to the repository root.

## Container Diagram

```
+-----------------------------------------------------------------+
| strict_module CLI                                               |
| Entrypoint: strict_module/cli.py :: main()                      |
+-----------------------------------------------------------------+
        |
        +-- sys.argv[1] == "loc-cap" ?
        |   yes: handle_loc_cap(sys.argv)
        |   +-----------------------------------------------------+
        |   | LOC cap (strict_loc_cap/loc_cap_client.py)          |
        |   | LocCap.run_loc_cap(path, hard_cap, soft_target,     |
        |   |                    baseline_file, generate)         |
        |   |   count_lines, load_baseline, find_python_files,    |
        |   |   generate_baseline                                 |
        |   +-----------------------------------------------------+
        |
        +-- no: standard linting
            +-----------------------------------------------------+
            | Config (strict_config/_config.py)                   |
            | Config.from_pyproject(path) -> Config               |
            | missing file: defaults; invalid: ConfigLoadError    |
            +-----------------------------------------------------+
                    |
                    v
            +-----------------------------------------------------+
            | Linter (strict_linter/linter_client.py)             |
            | DtoStrictLinter(config, baseline)                   |
            |   lint_path(path) -> list[Violation]                |
            |     lint_file(py_file) for each *.py                |
            |       read source      -> LintInputError on failure |
            |       ast.parse        -> LintInputError on failure |
            |       run CHECKER_CLASSES (R001..R015)              |
            |       drop disabled rules and baseline entries      |
            |     apply severity_overrides                        |
            |   format_violations(violations, format)             |
            |   get_exit_code(violations) -> int                  |
            +-----------------------------------------------------+
                    |
                    v
            print output to stdout; sys.exit(code)
```

## Flow Trace

### Entry Point and Subcommand Selection

1. **CLI entry** (`strict_module/cli.py::main()`)
   - `sys.argv[1] == "loc-cap"` -> `handle_loc_cap(sys.argv)`.
   - Otherwise the standard linting path runs.

### LOC Cap Subcommand

2. **Arguments** (`handle_loc_cap`)
   - Positional `path`; options `--config`, `--hard-cap`, `--soft-target`, `--baseline`, `--generate-baseline`.
   - `Config.from_pyproject(config_path)`; a `ConfigLoadError` prints the message to stderr and returns exit code 1.
   - CLI values override the `[tool.strict-module.loc-cap]` settings.

3. **Run** (`LocCap.run_loc_cap`)
   - `--generate-baseline`: `generate_baseline(path)` prints `path:loc` lines sorted by LOC descending and returns 0.
   - Check mode loads the baseline with `load_baseline(baseline_file)`:
     - A missing file yields an empty baseline. When the file name is the default `.loc-cap-baseline.txt`, the legacy names `.strict-module-baseline.txt` and `.dto-strict-baseline.txt` are tried in order.
     - A file that exists but cannot be decoded raises `LocCapInputError`.
   - `find_python_files(path)` walks `*.py`, skips the default exclude patterns (`migrations`, `management/commands`) and LOC test files (`conftest.py`, `test_*.py`, anything under `tests/`).
   - Each file is counted with `count_lines`, which uses `wc -l` semantics. A file that cannot be decoded raises `LocCapInputError`.
   - `LocCapInputError` from any step prints the message to stderr and returns exit code 1.
   - Classification per file:
     - `soft_target < loc <= hard_cap`: soft warning.
     - `loc > hard_cap` and not in the baseline: hard violation ("NEW OFFENDER").
     - `loc > hard_cap` and larger than its baseline value: hard violation ("grew by N").
     - Baseline entries that are deleted, or shrank below the hard cap: improvements.
   - Output uses GitHub annotation prefixes (`::warning::`, `::notice::`, `::error::`). Hard violations return 1. When nothing is over the cap the success line starts with `OK:` and the run returns 0.

### Standard Linting (Default Mode)

4. **Argument parsing** (`main()`)
   - Options: `path` (zero or more), `--config` (default `pyproject.toml`), `--format` (`text`, `github`, `json`), `--generate-baseline`, `--baseline`.
   - `Config.from_pyproject(Path(args.config))`; a `ConfigLoadError` exits 1.

5. **Generate baseline** (`--generate-baseline`)
   - Requires at least one PATH; otherwise prints an error and exits 1.
   - `_lint_all` lints every PATH. A `LintInputError` prints to stderr and exits 1.
   - `generate_baseline(violations)` emits one object per violation with `file`, `line`, `rule_id` and `message_hash` (the first 16 hex characters of the SHA-256 of the message). JSON goes to stdout and the run exits 0.

6. **Path check and baseline load**
   - Every PATH must exist; otherwise `ERR_NONEXISTENT_PATH` goes to stderr and the run exits 1.
   - With `--baseline`, `DtoStrictLinter.load_baseline(path)` returns a mapping keyed by `(file, line, rule_id)`. Any `BaselineLoadError` (missing or unreadable file, invalid JSON, non-list top level, non-object entry, missing key) prints to stderr and exits 1. On success the count goes to stderr through `MSG_BASELINE_LOADED`.
   - The stored `message_hash` is read but not compared; a baseline entry matches on file, line and rule only.

7. **Lint** (`DtoStrictLinter.lint_path(path)` for each PATH)
   - A file path is linted directly. A directory is walked with `rglob("*.py")`; test files are included in the walk and exempted by the checkers themselves.
   - Each file goes through `lint_file`:
     - A suffix other than `.py` returns no violations.
     - `read_text()` failure (OSError, UnicodeDecodeError) raises `LintInputError` with `ERR_SOURCE_UNREADABLE`.
     - `ast.parse` failure (SyntaxError, ValueError) raises `LintInputError` with `ERR_SOURCE_SYNTAX`.
     - Each class in `CHECKER_CLASSES` (R001 through R015) is constructed as `Checker(path, source, config)`, walks the tree and contributes its violations.
     - `_filter` drops violations of rules in `disabled_rules`, then drops violations whose `(file, line, rule_id)` is in the baseline.
   - `lint_path` applies `severity_overrides` to each violation. Valid overrides are the names HIGH, MEDIUM, LOW and INFO (case-insensitive); other values are ignored.
   - `LintInputError` propagates out of `lint_path`; the CLI prints it to stderr and exits 1, so an unreadable or unparseable input never passes.

8. **Checkers** (`strict_checkers/r001.py` ... `r015.py`, all subclasses of `BaseChecker`)

   | Rule | Severity | What it checks | Scope |
   | --- | --- | --- | --- |
   | R001 | HIGH | `Dict[str, Any]` (or a bare `dict`/`list`/`tuple` when `strict_collections` is on) in signatures | service paths |
   | R002 | MEDIUM | inline dict literal with `min_dict_keys` or more string keys, unless tagged | service files |
   | R003 | MEDIUM | dataclass shape: `frozen`, `slots`, and `repr` according to `r003_mode` | DTO paths |
   | R004 | HIGH | facade: module-level function whose body is only a delegation to a class method | service paths |
   | R005 | LOW | `validate_*` with a `payload` parameter that does not call `from_dict()` or raise a validation error | all |
   | R006 | HIGH | `typing.Any` in signatures | service paths (`r006_paths`) |
   | R007 | MEDIUM | `@pytest.fixture` outside `conftest.py` | test files |
   | R008 | MEDIUM | module-level `test_*` function | test files |
   | R009 | INFO | module-level function without a recorded reason | non-test files |
   | R010 | MEDIUM | legacy `typing` ABC aliases (use `collections.abc`) | all |
   | R011 | HIGH | string literal at a `raise` site (use a named constant) | non-test files, constants modules exempt |
   | R012 | INFO | call that fits on one line but is split across lines | all |
   | R013 | INFO | multi-parameter signature not grouped 2-3 per line | all |
   | R014 | INFO | multi-keyword call not grouped | all |
   | R015 | INFO | try/except statement-count asymmetry | all |

   - R004 detail (`R004Checker`): only module-level functions in service paths are considered. The body, after an optional docstring, must be one of:
     - a single `return Name.method(...)`, `return Name(...).method(...)` or `return Name().method(...)`, or a bare `Name.method(...)` expression statement;
     - `instance = Name(...)` followed by `return instance.method(...)`.
     `Name` must start with a capital letter. Any other shape is not a facade and is left to R009.
   - R009 detail (`R009Checker`): exempt shapes are test files; functions with any decorator; `main` and `handle_*`; dunder module hooks (for example `__getattr__`, `__dir__`); `pytest_*` hooks; and functions carrying an exception tag on the def line or in the first docstring line. The default tag is `module-level:`, matched case-insensitively.
   - Exception tags (`has_exception_tag`) are read from the def line and the first docstring line only. The default tags are `facade - celery schedule`, `FRAMEWORK` and `module-level:`. Setting `exception_tags` replaces the defaults.

9. **Suppression** (`AnnotationInspector.has_noqa_comment`, per node line)
   - `# noqa` with no codes suppresses every rule.
   - `# noqa: strict-module` or `# noqa: dto-strict` suppresses every rule.
   - `# noqa: strict-module-R001`, `# noqa: dto-strict-R001` and `# noqa: R001` suppress that rule.

### Output and Exit

10. **Format** (`DtoStrictLinter.format_violations`)
    - `text`: `file:line: RULE message`.
    - `github`: `::error file=...,line=...,col=...::message` for HIGH, `::notice` for INFO, `::warning` otherwise.
    - `json`: an array of objects with `rule_id`, `severity`, `file`, `line`, `col`, `message`.

11. **Exit code** (`DtoStrictLinter.get_exit_code`)
    - No violations: 0.
    - Any HIGH: 1.
    - Otherwise any MEDIUM: 2.
    - Otherwise any LOW: 3.
    - INFO-only results return 0, so R009 and the R012-R015 formatting rules never block.

12. **Print and exit**: `main()` prints the formatted violations to stdout (when there are any) and returns the exit code.

## Real Output Examples

The examples below were run against the 0.6.0 tree. The paths are the paths passed on the command line, relative to the directory the command ran in. The first path segments follow the default `service_paths` pattern `**/services/*.py`.

### Clean file

```
$ uv run strict-module tools/clean.py
EXIT CODE: 0
```

A file that matches no rule prints nothing and exits 0.

### Service file with a HIGH finding

```
$ uv run strict-module apps/demo/services/handler.py
apps/demo/services/handler.py:6: R001 Dict[str, Any] in signature: handle_request
apps/demo/services/handler.py:6: R006 typing.Any in parameter: handle_request
EXIT CODE: 1
```

`params: Dict[str, Any]` triggers R001 (HIGH) and R006 (HIGH). Exit code 1 because HIGH findings are present.

### Facade in a service path

```
$ uv run strict-module apps/demo/services/facade.py
apps/demo/services/facade.py:12: R004 Facade 'get_user': module-level wrapper around UserService.get_user; call the class method directly or move the logic onto the class. A framework-required wrapper carries an exception tag (for example '# FRAMEWORK').
apps/demo/services/facade.py:12: R009 Module-level function 'get_user': a method on a class is the default shape. Keep it module-level only when that is the optimal shape (framework hook, entry point, stateless helper with no owning class) and record why with '# module-level: <reason>' on the def line. Entry points need no tag: main, handle_*.
EXIT CODE: 1
```

`return UserService().get_user(user_id)` is the facade shape, so R004 (HIGH) fires. The same function also gets the R009 advisory, which does not change the exit code on its own.

### Module-level helper outside a service path

```
$ uv run strict-module tools/helpers.py
tools/helpers.py:4: R009 Module-level function 'scale_value': a method on a class is the default shape. Keep it module-level only when that is the optimal shape (framework hook, entry point, stateless helper with no owning class) and record why with '# module-level: <reason>' on the def line. Entry points need no tag: main, handle_*.
EXIT CODE: 0
```

Only INFO findings are present, so the run exits 0.

### File that cannot be parsed

```
$ uv run strict-module apps/demo/services/broken.py
error: cannot parse Python source: apps/demo/services/broken.py line 1: invalid syntax (<unknown>, line 1)
EXIT CODE: 1
```

The error goes to stderr. The run exits 1 instead of reporting the file as clean.

## LOC Cap Flow Summary

`loc-cap` reads the configuration, scans the tree, compares each counted file with the ratchet baseline and reports soft warnings, improvements and hard violations. Unreadable files and baselines stop the run with an error and exit 1.

## Summary

strict_module runs two independent paths:

1. **Standard linting** (default): Config -> R001-R015 checkers -> disabled-rule and baseline filter -> severity overrides -> format -> exit code.
2. **LOC cap** (`loc-cap`): Config -> file scanner -> line count -> baseline comparison -> annotated report -> exit code.

**Key design points**:

- Checkers are path-aware (`service_paths`, `dto_paths`, `r006_paths`, test-file patterns).
- Suppression is inline per node; exception tags are comments on the def line or in the first docstring line.
- Baseline ratcheting accepts recorded violations on file, line and rule; new violations still fail.
- Exit codes reflect the most severe blocking finding: 0 clean or INFO-only, 1 HIGH, 2 MEDIUM, 3 LOW.
- Unreadable or unparseable inputs are errors, not skips: they print to stderr and exit 1.
