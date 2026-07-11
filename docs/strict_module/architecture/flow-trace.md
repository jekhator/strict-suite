# strict_module Flow-Trace Diagram

strict_module is a CLI linter tool (not a decorator) that enforces Python DTO + facade discipline via AST analysis. It can run in two modes: standard linting or LOC cap checking. This diagram traces the actual execution path.

## Container Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ strict_module / dto-strict CLI                                  │
│ Entrypoint: cli.py :: main()                                    │
└─────────────────────────────────────────────────────────────────┘
        │
        ├─▶ [SUBCOMMAND?] sys.argv[1] == 'loc-cap'
        │   ┌─────────────────────────────────────────────────────┐
        │   │ LOC Cap Enforcer (loc_cap.py)                       │
        │   │ ├─ count_lines(file_path) → int                     │
        │   │ ├─ load_baseline(baseline_file) → dict[str, int]    │
        │   │ ├─ find_python_files(root, patterns) → dict[str, int]
        │   │ ├─ generate_baseline(root) → str                    │
        │   │ └─ run_loc_cap(path, hard, soft, baseline) → int    │
        │   └─────────────────────────────────────────────────────┘
        │
        └─▶ [DEFAULT] Standard linting mode
            ┌─────────────────────────────────────────────────────┐
            │ Config Loading (config/_config.py)                  │
            │ ├─ Config.from_pyproject(path: Path) → Config       │
            │ ├─ Parses [tool.strict-module] or [tool.dto-strict] │
            │ ├─ Loads: service_paths, dto_paths, exception_tags  │
            │ ├─       disabled_rules, r003_mode, loc_cap config  │
            │ └─ Fallback: default Config() if load fails         │
            └─────────────────────────────────────────────────────┘
                    │
                    ▶ DtoStrictLinter(config, baseline?)
            ┌─────────────────────────────────────────────────────┐
            │ Linter Engine (linter.py)                           │
            │ ├─ lint_path(path: Path) → list[Violation]          │
            │ ├─   walk(path.rglob("*.py"))                       │
            │ ├─   lint_file(py_file: Path) → list[Violation]     │
            │ │     ├─ read_text() ⚠ OSError/UnicodeDecodeError → skip
            │ │     ├─ ast.parse(source) ⚠ SyntaxError → skip     │
            │ │     ├─ for each Checker in [R001..R008]:          │
            │ │     │   ├─ checker = RxxxChecker(path, src, cfg)  │
            │ │     │   ├─ checker.visit(tree) [AST walk]         │
            │ │     │   └─ violations += checker.violations        │
            │ │     ├─ filter by config.is_rule_enabled()         │
            │ │     └─ filter by baseline (ratchet) ← new vs old   │
            │ │                                                    │
            │ ├─ Checkers (checkers.py):                          │
            │ │   ├─ R001Checker: Dict[str, Any] in service sigs  │
            │ │   ├─   ⚠ Guard: is_service_path(...) + not noqa   │
            │ │   ├─ R002Checker: inline dict 3+ keys             │
            │ │   ├─   ⚠ Guard: in_service_file + skip annotated  │
            │ │   ├─       constants + skip serializer returns    │
            │ │   ├─ R003Checker: dataclass repr=False (anti-can) │
            │ │   ├─   ⚠ Guard: is_dto_path() + r003_mode         │
            │ │   ├─ R004Checker: module-level fn w/o exception   │
            │ │   ├─   ⚠ Guard: is_service_path() + not wrapper   │
            │ │   ├─ R005Checker: validator not using from_dict() │
            │ │   ├─   ⚠ Guard: starts with validate_ + payload   │
            │ │   ├─ R006Checker: typing.Any in service sigs      │
            │ │   ├─   ⚠ Guard: is_service_path() + not noqa      │
            │ │   ├─ R007Checker: fixture outside conftest.py     │
            │ │   ├─   ⚠ Guard: is_test_file() + not conftest     │
            │ │   └─ R008Checker: bare module test_* functions    │
            │ │       ⚠ Guard: is_test_file() + not noqa          │
            │ │                                                    │
            │ └─ Violation(rule_id, severity, file, line, col,   │
            │     message)                                        │
            └─────────────────────────────────────────────────────┘
                    │
                    ▶ severity_overrides(rule_id) → update severity
                    │
                    ▶ format_violations(violations, format)
            ┌─────────────────────────────────────────────────────┐
            │ Output Formatters (linter.py)                       │
            │ ├─ text: file:line: rule_id message                 │
            │ ├─ github: ::error file=...,line=...,col=... ::msg  │
            │ └─ json: [{rule_id, severity, file, line, col, ...}]
            └─────────────────────────────────────────────────────┘
                    │
                    ▶ get_exit_code(violations) → int
            ┌─────────────────────────────────────────────────────┐
            │ Exit Code Logic (linter.py)                         │
            │ ├─ no violations → 0 (SUCCESS)                      │
            │ ├─ any HIGH severity → 1 (HARD FAIL)                │
            │ ├─ any MEDIUM severity → 2 (WARN)                   │
            │ └─ only LOW severity → 3 (INFO)                     │
            └─────────────────────────────────────────────────────┘
                    │
                    ▶ print(output)
                    │
                    ▶ sys.exit(code)
```

## FLOW TRACE

### Entry Point & Dispatch

1. **CLI Entry** (`cli.py::main()`)
   ├─ Check `sys.argv[1]` for subcommand
   └─ `loc-cap` present?
      ├─ YES: handle_loc_cap(sys.argv)
      │  ├─ Parse loc-cap args: path, --config, --hard-cap, --soft-target, --baseline, --generate-baseline
      │  ├─ Load Config.from_pyproject(config_path)
      │  └─ Call run_loc_cap(...) ── returns exit code (0 clean, 1 violations)
      │
      └─ NO: Standard linting mode

### Standard Linting (Default Mode)

2. **Argument Parsing** (`cli.py::main()`)
   ├─ Parse: path (required), --config (default: pyproject.toml), --format (text/github/json), --baseline (optional), --generate-baseline
   └─ Load Config.from_pyproject(Path(args.config))
      ├─ Read TOML file ⚠ OSError → return Config()
      ├─ Extract [tool.strict-module] or [tool.dto-strict]
      └─ Return Config(service_paths=..., dto_paths=..., exception_tags=..., r003_mode=..., loc_cap=..., ...)

3. **Generate Baseline Branch** (if --generate-baseline flag)
   ├─ Require PATH argument (error if missing)
   ├─ For each path in args.path:
   │  ├─ Create DtoStrictLinter(config)
   │  └─ all_violations.extend(linter.lint_path(target_path))
   ├─ baseline_data = linter.generate_baseline(all_violations)
   │  └─ For each violation: {file, line, rule_id, message_hash (SHA256[:16])}
   ├─ Print JSON (stdout)
   └─ sys.exit(0)

4. **Standard Lint Branch** (no --generate-baseline)
   ├─ Require PATH argument (error if missing)
   ├─ Load baseline (if --baseline provided)
   │  └─ DtoStrictLinter.load_baseline(baseline_path) → dict[(file, line, rule_id)] -> message_hash
   │     ⚠ Exception → return {}
   └─ Create DtoStrictLinter(config, baseline=baseline)

### Linting Pipeline

5. **Lint All Paths** (`linter.py::lint_path()`)
   ├─ For each path_str in args.path:
   │  ├─ target_path = Path(path_str)
   │  ├─ path.is_file()? → lint_file(path) → list[Violation]
   │  └─ path.is_dir()? → for each py in path.rglob("*.py"): lint_file(py)
   │
   └─ all_violations = combine results

6. **Lint Single File** (`linter.py::lint_file()`)
   ├─ file_path.suffix != ".py"? → return []
   ├─ source = file_path.read_text()
   │  └─ ⚠ Exception (OSError, UnicodeDecodeError) → return []
   ├─ tree = ast.parse(source)
   │  └─ ⚠ SyntaxError → return []
   │
   └─ For each Checker class in [R001, R002, R003, R004, R005, R006, R007, R008]:
      ├─ checker = RxxxChecker(file_path, source, config)
      ├─ checker.visit(tree) [AST walk with visitor pattern]
      └─ violations.extend(checker.violations)

7. **Checker Execution** (each RxxxChecker inherits from ast.NodeVisitor)
   └─ Per rule:
      │
      ├─ R001Checker::visit_FunctionDef():
      │  ├─ is_service_path(file_path, config.service_paths)? → NO: return
      │  ├─ is_suppressed(node, "R001")? ← has_noqa_comment(...) → YES: return
      │  └─ For each param/vararg/kwarg/return annotation:
      │     ├─ is_dict_str_any(annotation)? → Violation(R001, HIGH, ...)
      │     └─ config.strict_collections & is_bare_collection(annotation)? → Violation(R001, HIGH, ...)
      │
      ├─ R002Checker::visit_Dict():
      │  ├─ in_service_file? → NO: return
      │  ├─ is_suppressed(node, "R002")? → YES: return
      │  ├─ _is_annotated_constant(dict)? ← module-level typed const → YES: skip
      │  ├─ _is_serializer_return_dict(dict)? ← to_* return in dataclass → YES: skip
      │  ├─ Count string keys >= config.min_dict_keys?
      │  │  ├─ NO: skip
      │  │  └─ YES: check for exception_tags in comment
      │  │     ├─ has_tag? → validate justification (if required) → check max_count
      │  │     │  ├─ NO justification: Violation(R002, MEDIUM, ...)
      │  │     │  └─ Exceeded max_tags: Violation(R002, MEDIUM, ...)
      │  │     └─ NO tag: Violation(R002, MEDIUM, ...)
      │
      ├─ R003Checker::visit_ClassDef():
      │  ├─ is_dto_path(file_path, config.dto_paths)? → NO: return
      │  ├─ is_suppressed(node, "R003")? → YES: return
      │  ├─ @dataclass decorator present?
      │  │  └─ Extract kwargs (frozen, slots, repr)
      │  │     ├─ r003_mode == "canonical":
      │  │     │  ├─ r003_strict_repr? → check repr != False → Violation(R003, MEDIUM, ...)
      │  │     │  └─ else (relaxed): check frozen+slots → Violation(R003, MEDIUM, ...)
      │  │     └─ r003_mode == "legacy": check frozen+slots+repr=False → Violation(R003, MEDIUM, ...)
      │
      ├─ R004Checker::visit_Module():
      │  ├─ is_service_path(file_path, config.service_paths)? → NO: return
      │  └─ For each top-level FunctionDef:
      │     ├─ is_suppressed(node, "R004")? → YES: continue
      │     └─ _has_exception_tag(fn)? | _is_class_method_wrapper(fn)?
      │        ├─ NO: Violation(R004, HIGH, ...)
      │        └─ YES: skip
      │
      ├─ R005Checker::visit_FunctionDef():
      │  ├─ node.name.startswith("validate_")? → NO: return
      │  ├─ is_suppressed(node, "R005")? → YES: return
      │  ├─ Has "payload" parameter?
      │  │  └─ _has_from_dict_call(fn)? | _has_validation_error(fn)?
      │  │     ├─ NO: Violation(R005, LOW, ...)
      │  │     └─ YES: skip
      │
      ├─ R006Checker::visit_FunctionDef():
      │  ├─ is_service_path(file_path, config.r006_paths)? → NO: return
      │  ├─ is_suppressed(node, "R006")? → YES: return
      │  └─ For each param/vararg/kwarg/return annotation:
      │     ├─ contains_any(annotation)? → Violation(R006, HIGH, ...)
      │
      ├─ R007Checker::visit_FunctionDef():
      │  ├─ is_test_file(file_path)? → NO: return
      │  ├─ file_path.name == "conftest.py"? → YES: return (allowed)
      │  └─ Has @pytest.fixture decorator?
      │     ├─ is_suppressed(node, "R007")? → YES: continue
      │     └─ Violation(R007, MEDIUM, ...)
      │
      └─ R008Checker::visit_Module():
         ├─ is_test_file(file_path)? → NO: return
         └─ For each top-level FunctionDef starting with "test_":
            ├─ is_suppressed(node, "R008")? → YES: continue
            └─ Violation(R008, MEDIUM, ...)

### Filtering & Baseline

8. **Filter by Enabled Rules** (`linter.py::lint_path()`)
   └─ For each violation:
      ├─ config.is_rule_enabled(rule_id)? ← rule_id not in disabled_rules
      │  ├─ YES: keep
      │  └─ NO: discard

9. **Apply Baseline (Ratchet Mode)** (`linter.py::_filter_by_baseline()`)
   └─ For each violation:
      ├─ key = (violation.file, violation.line, violation.rule_id)
      ├─ key in self.baseline?
      │  ├─ YES: discard (violation was accepted in baseline)
      │  └─ NO: keep (new violation)

10. **Apply Severity Overrides** (`linter.py::lint_path()`)
    └─ For each violation with rule_id in config.severity_overrides:
       └─ Create new Violation with updated severity

### Output & Exit

11. **Format Violations** (`linter.py::format_violations()`)
    └─ args.format type?
       ├─ "text": for each v: "{file}:{line}: {rule_id} {message}"
       ├─ "github": for each v: "::{level} file={file},line={line},col={col}::{message}"
       │  └─ level = "error" if severity==HIGH else "warning"
       └─ "json": all violations as JSON array with rule_id, severity, file, line, col, message

12. **Compute Exit Code** (`linter.py::get_exit_code()`)
    ├─ no violations? → return 0 ← EXIT 0 (SUCCESS)
    ├─ any HIGH severity? → return 1 ← EXIT 1 (HARD FAIL)
    ├─ any MEDIUM severity? → return 2 ← EXIT 2 (WARN)
    └─ only LOW severity? → return 3 ← EXIT 3 (INFO)

13. **Print & Exit** (`cli.py::main()`)
    ├─ print(output) [formatted violations to stdout]
    └─ sys.exit(code)

---

## REAL OUTPUT EXAMPLES

### Clean File Test
```bash
$ cd /tmp/claude-flowtrace/strict-suite-work
$ uv run strict-module /tmp/test_clean.py
[no output]
EXIT CODE: 0
```

**Explanation**: File matches no patterns (not in services/, not in dtos/), so all checkers skip. No violations collected. Exit code 0 (success).

### Violation File Test
```bash
$ cd /tmp/claude-flowtrace/strict-suite-work
$ uv run strict-module /tmp/app_test
/tmp/app_test/services/handler.py:5: R001 Dict[str, Any] in signature: handle_request
/tmp/app_test/services/handler.py:5: R004 Module-level def without exception tag: handle_request
/tmp/app_test/services/handler.py:5: R006 typing.Any in parameter: handle_request
EXIT CODE: 1
```

**Explanation**:
- File path matches `**/services/*.py` pattern (in_service_file=True).
- R001: `params: Dict[str, Any]` triggers is_dict_str_any() check → Violation(HIGH).
- R004: Module-level function `handle_request` has no exception tag and is not a wrapper → Violation(HIGH).
- R006: `params: Dict[str, Any]` contains "Any" → Violation(HIGH).
- Exit code 1 because has_high=True in get_exit_code().

---

## Noqa Suppression (example path)

For any node with matching rule:
- `# noqa` → suppress all rules
- `# noqa: strict-module` → suppress all strict-module rules
- `# noqa: strict-module-R001` → suppress R001 specifically
- `# noqa: dto-strict` (backward-compat) → suppress all rules
- `# noqa: dto-strict-R001` (backward-compat) → suppress R001

---

## LOC Cap Flow (loc_cap.py subcommand)

1. **Subcommand Detection** (`cli.py::main()`)
   └─ sys.argv[1] == "loc-cap"? → handle_loc_cap(sys.argv)

2. **LOC Cap Args** (`cli.py::handle_loc_cap()`)
   ├─ Parse: path, --config, --hard-cap, --soft-target, --baseline, --generate-baseline
   ├─ Load Config.from_pyproject(config_path)
   └─ Merge CLI args with config.loc_cap settings

3. **Run LOC Cap** (`loc_cap.py::run_loc_cap()`)
   ├─ generate? → generate_baseline(path) → print() → exit(0)
   │
   └─ Check mode:
      ├─ baseline = load_baseline(baseline_file)
      │  └─ Fallback: .strict-module-baseline.txt, .dto-strict-baseline.txt
      │     ⚠ OSError → return {}
      │
      ├─ current = find_python_files(path, exclude_patterns)
      │  └─ For each *.py:
      │     ├─ Skip migrations/, management/commands, test files
      │     ├─ loc = count_lines(file) ← wc -l semantics ⚠ OSError/UnicodeDecodeError → 0
      │     └─ current[file] = loc
      │
      ├─ For each current file:
      │  ├─ soft_target < loc <= hard_cap? → soft_warnings.append(...)
      │  └─ loc > hard_cap?
      │     ├─ NOT in baseline? → hard_violations.append("NEW OFFENDER")
      │     └─ loc > baseline[file]? → hard_violations.append("grew by {delta}")
      │
      ├─ For each baseline file:
      │  └─ NOT in current? OR improved? → improvements.append(...)
      │
      └─ Print results:
         ├─ soft_warnings? → ::warning::
         ├─ improvements? → ::notice::
         ├─ hard_violations? → ::error:: → return 1
         └─ else: ✓ all clean → return 0

---

## Summary

strict_module operates in **two independent paths**:

1. **Standard Linting** (default): Config → AST checkers (R001-R008) → baseline ratchet → severity overrides → format → exit code
2. **LOC Cap** (subcommand): Config → file scanner → count lines → baseline compare → report violations → exit code

**Key Design Points**:
- All checkers are **path-aware** (service_paths, dto_paths, test_file patterns).
- **Noqa suppression** is inline per node; exception tags are inline comments.
- **Baseline ratcheting** allows accepted violations; new ones still fail.
- **Exit codes** reflect severity: 0=clean, 1=HIGH, 2=MEDIUM, 3=LOW.
- **File I/O errors** (OSError, UnicodeDecodeError) silently skip files.
- **Syntax errors** in Python files are silently skipped (linter continues).
