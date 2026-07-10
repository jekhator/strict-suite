# Linter Rules Engine - Code Review

**Date:** 2026-07-09
**Component:** strict_module/rules.py, strict_module/checkers.py
**Focus:** Architecture, rule definitions, AST visitor patterns

## Architecture

The engine uses separate checker classes for each rule (R001-R008), each implementing an ast.NodeVisitor subclass. This single-rule-per-class design decouples rule logic and simplifies testing.

Rule definitions are centralized in RuleRegistry as frozen dataclasses. The registry is the source of truth for rule metadata (ID, name, severity, description).

Assessment: Architecture is sound. Single-responsibility separation enables independent rule modification and testing.

## Rule Implementations

Each checker receives file path and source code, parses the source as AST, and traverses nodes to detect violations. Visitor methods (visit_FunctionDef, visit_ClassDef, etc.) match node types to rule logic.

Common patterns:
- R001: Checks function signatures for Dict[str, Any] or bare collections.
- R002: Scans for inline dict literals with 3+ string keys.
- R003-R008: Validate dataclass patterns, fixture definitions, test organization.

Assessment: Rule logic is domain-specific and correct. Patterns are consistent across implementations.

## Violation Collection

Violations are immutable Violation dataclasses with frozen=True and slots=True. Each violation records rule ID, severity, file, line, column, and message.

Two output formats: format_text() for plain text, format_github() for GitHub Actions annotations.

Assessment: Immutable violation design prevents mutation after creation. Dual format support is clean and necessary for CI integration.

## Baseline and Comment Tracking

The R002Checker tracks function comments and dict parent nodes to suppress violations on tagged lines. Comments are extracted from source lines and stored by node ID.

Assessment: Comment handling is locale-aware (comment text stored as strings). Parent tracking via dict_parents allows context-sensitive rule application.

## Type Annotations

Type hints are present on function signatures and return types. Local variable annotations added for clarity.

Assessment: Type annotations are sufficient for static type-checking and improve maintainability.

## Conclusion

The rules engine implementation is well-structured, domain-correct, and maintainable. Checker separation, immutable violation records, and dual output format support are design strengths.

No significant code quality issues identified.
