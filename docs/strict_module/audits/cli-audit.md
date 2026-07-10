# CLI - Security Audit

**Date:** 2026-07-09
**Component:** strict_module/cli.py
**Scope:** Command-line argument parsing and subcommand dispatch

## Security Assessment

The CLI module provides command-line entry points for the linter and LOC cap subcommands. This audit evaluates argument parsing safety, dispatch logic, and error handling.

### Argument Parsing (argparse)

The CLI uses argparse.ArgumentParser to parse command-line arguments. Main arguments include:
- path: Directory to lint
- --config: Path to pyproject.toml (default: pyproject.toml)
- --format: Output format (plain, github; default: plain)
- --baseline: Baseline file path (default: .loc-cap-baseline.txt)
- Other LOC cap flags (--hard-cap, --soft-target, --generate-baseline)

Security considerations:
- Argument values are strings; no shell injection via argument parsing.
- Path arguments are passed directly to pathlib.Path(), which performs no glob expansion or shell interpretation.
- Format argument is validated against a fixed set of options.

No injection vulnerabilities identified.

### Subcommand Dispatch

The main() function checks sys.argv[1] to detect "loc-cap" subcommand. If present, handle_loc_cap() is called; otherwise, the linter subcommand is executed.

Security considerations:
- Dispatch is string-based; no dynamic code loading.
- sys.argv parsing is direct; no environment variable expansion.
- Subcommand handlers are hardcoded functions, not dynamically loaded.

No code injection or privilege escalation risks.

### File Path Handling

File paths passed as arguments are resolved using pathlib.Path. No relative-path traversal or symlink expansion is performed by the CLI; Path is used as-is.

Security observation: Caller is responsible for path safety (e.g., ensuring paths are within intended scope).

### Return Codes

Both subcommands return exit codes: 0 for success, non-zero for failure. Exit codes are propagated directly from sys.exit() or the handler return value.

Assessment: Exit code semantics are standard and correct.

## Conclusion

Argument parsing is safe from injection. Subcommand dispatch is direct and does not involve dynamic code loading. Path handling delegates to caller.

No security vulnerabilities identified in CLI module.
