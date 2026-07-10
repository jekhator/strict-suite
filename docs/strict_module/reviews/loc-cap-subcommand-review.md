# LOC Cap Subcommand - Code Review

**Date:** 2026-07-09
**Component:** strict_module/loc_cap.py, strict_module/cli.py
**Focus:** Implementation, baseline semantics, and CLI integration

## Architecture

The LOC cap enforcer is split into three concerns:
- `loc_cap.py`: Core logic for file discovery, line counting, and baseline comparison.
- `cli.py`: Argument parsing and subcommand dispatch (handle_loc_cap, main).
- `LocCapConfig`: Dataclass for configuration storage (hard_cap, soft_target, baseline_file).

Assessment: Separation is clean. LOC cap logic is independent of CLI layer, enabling reuse.

## File Discovery

find_python_files() uses pathlib for traversal and applies exclusion patterns as substring matches. Test files are detected by name (conftest.py, test_*.py) and location (tests/ directory).

Strengths:
- Absolute path normalization via resolve() prevents symlink confusion.
- Exclusion patterns are hardcoded (migrations, management/commands), not user-configurable.
- Test detection is built-in, avoiding double-counting.

Assessment: Implementation is straightforward and correct.

## LOC Counting

count_lines() reads files as UTF-8 and counts lines. Encoding errors are caught and treated as 0 lines.

Consideration: Files that are not UTF-8 (e.g., binary, Latin-1) will be skipped. For Python source, UTF-8 is standard; this is acceptable.

Assessment: Implementation matches wc -l semantics for baseline compatibility.

## Baseline Persistence

load_baseline() reads baseline files in key-value format (path: loc_count). Fallback names allow migration from legacy baseline file names.

Strengths:
- Fallback logic supports incremental migration (dto-strict -> strict-module).
- Malformed files are skipped without crashing.
- Baseline is text, not serialized objects; human-readable and git-friendly.

Assessment: Baseline design is robust and backward-compatible.

## Ratcheting Enforcement

The LOC cap enforcer compares baseline to current LOC counts:
- Hard cap: Fail if current exceeds hard cap.
- Soft target: Warn (but pass) if between soft target and hard cap.
- Regression: Fail if current exceeds baseline (ratchet effect).

Strength: Ratcheting prevents silent baseline creep; changes require explicit --generate-baseline approval.

Assessment: Ratcheting logic is correct and serves the intended goal.

## CLI Integration

handle_loc_cap() dispatches based on sys.argv[1] == 'loc-cap'. Subcommand arguments are parsed separately; config is loaded from pyproject.toml, with CLI flags overriding config file values.

Assessment: Dispatch logic is clear. Config layering (CLI > file > default) is intuitive.

## Conclusion

The LOC cap subcommand is well-implemented. File discovery is safe, baseline handling is robust, and ratcheting enforces discipline.

No significant code quality issues identified.
