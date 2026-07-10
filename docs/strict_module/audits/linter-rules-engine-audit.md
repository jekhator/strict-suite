# Linter Rules Engine - Security Audit

**Date:** 2026-07-09
**Component:** strict_module/rules.py, strict_module/checkers.py
**Scope:** R001-R008 rule implementations and AST-based violation detection

## Security Assessment

The linter rules engine is an AST-based checker that identifies eight categories of Python code pattern violations related to DTO discipline and facade enforcement. This audit evaluates the mechanisms by which rules are defined, discovered, and reported.

### Rule Registry (rules.py::RuleRegistry)

The registry centralizes rule definitions as frozen dataclasses (R001-R008). Each rule specifies ID, name, severity, and description. The registry is immutable and complete at import time.

Security posture: The rule definitions are static and cannot be modified at runtime, preventing rule injection or tampering.

### Checker Implementation (checkers.py)

Eight separate checker classes (R001Checker through R008Checker) inherit from BaseChecker and implement rule-specific AST visitor methods.

Security considerations:
- AST visitors operate on Python source code parsed in isolation per file.
- Violations are collected in memory during traversal and returned as frozen Violation dataclasses.
- No arbitrary code execution occurs; only AST inspection.
- File paths are preserved as strings; no symlink resolution or traversal beyond the scanned tree.

### Violation Reporting

Violations are immutable frozen dataclasses containing rule ID, severity, file path, line and column numbers, and message text. Format methods support plain-text and GitHub Actions annotation output.

Potential issue: File paths in violations reflect the path argument passed to the checker; symlink normalization is caller's responsibility.

### Baseline Handling (linter.py::BaselineEntry)

Baseline entries track accepted violations by (file, line, rule_id, message_hash). Baselines allow suppression of known violations.

Security observation: Baselines are stored as dictionaries keyed by (file, line, rule_id) tuple; message hash prevents collisions if violation text changes.

## Conclusion

The rules engine provides read-only AST inspection without arbitrary execution. Immutable dataclass design prevents mutation of rule definitions or violation records. Severity assignments are hardcoded per rule, preventing escalation by external input.

No security vulnerabilities identified in rule registry, checker implementations, or violation reporting mechanisms.
