# LOC Cap Subcommand - Security Audit

**Date:** 2026-07-09
**Component:** strict_module/loc_cap.py, strict_module/cli.py
**Scope:** Line-of-code counting, baseline persistence, and enforcement

## Security Assessment

The LOC cap subcommand enforces line-of-code limits on Python source files with a ratchet baseline mechanism to prevent regression. This audit evaluates file I/O, baseline handling, and counting logic.

### File Discovery (find_python_files)

The function traverses a directory tree using pathlib.Path.rglob() to locate Python files. It applies exclusion patterns (migrations, management/commands) and test-file filters to produce a LOC count dictionary.

Security considerations:
- Path normalization uses Path.resolve() to convert to absolute paths, preventing symlink confusion.
- Exclusion patterns are string-based substring matching; no glob expansion.
- Test files (conftest.py, test_*.py, tests/ directories) are excluded automatically.

No arbitrary symlink resolution; path handling is safe.

### Baseline File I/O (load_baseline)

Baseline files are read as plain text, parsing lines in format "path: loc_count". Fallback logic attempts to load legacy baseline files (.strict-module-baseline.txt, .dto-strict-baseline.txt) if the primary name does not exist.

Security considerations:
- File I/O catches OSError and UnicodeDecodeError; malformed files are ignored gracefully.
- Baseline paths are not expanded via shell or environment variables; they are literal filesystem paths.
- No arbitrary code execution; baseline is parsed as text only.

Parsing is resilient; exceptions do not crash the checker.

### LOC Counting (count_lines)

The count_lines function opens a file and counts lines via sum(1 for _ in f). Semantics match wc -l for baseline compatibility.

Security considerations:
- File encoding is UTF-8; non-UTF-8 files raise UnicodeDecodeError and return 0.
- Counting is read-only; no file modification.
- Empty and non-existent files return 0 gracefully.

No file modification or encoding injection risks.

### Baseline Ratcheting

Baselines enforce a hard cap and soft target. If current LOC exceeds hard cap, the check fails. If between soft and hard, a warning is issued but check passes. Baseline permits regression only if previous baseline is absent or explicitly regenerated.

Security observation: Baseline provides change validation; new files or removed content requires explicit baseline update via --generate-baseline flag.

## Conclusion

File discovery is symlink-safe. Baseline I/O is exception-safe and text-only. LOC counting is read-only. Ratcheting logic prevents silent regression.

No security vulnerabilities identified in LOC cap subcommand implementation.
