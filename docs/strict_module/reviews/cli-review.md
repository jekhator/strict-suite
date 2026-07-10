# CLI - Code Review

**Date:** 2026-07-09
**Component:** strict_module/cli.py
**Focus:** Interface design, argument handling, and subcommand architecture

## Interface Design

The CLI exposes two subcommands via dispatch:
1. `strict-module <path>`: Linter subcommand (default)
2. `strict-module loc-cap <path>`: LOC cap subcommand

Main arguments for linter:
- path: Directory to scan
- --config: Path to config file (default: pyproject.toml)
- --format: Output format (plain, github; default: plain)
- --baseline: Baseline file (default: .loc-cap-baseline.txt)

Assessment: Interface is clean. Positional path argument is intuitive. Format options match GitHub Actions annotation style.

## Subcommand Dispatch

main() checks sys.argv[1] for "loc-cap" string. If found, handle_loc_cap() is called; otherwise, linter is invoked.

Assessment: Early dispatch via string check is explicit and efficient. Alternative would be argparse subparsers; current approach is simpler for two subcommands.

## Argument Parsing Strategy

Linter uses argparse.ArgumentParser with standard options. LOC cap dispatch happens before argparse initialization, avoiding conflicts between linter and LOC cap arguments.

Strength: Two separate parsers (linter in main(), LOC cap in handle_loc_cap()) avoid mutual interference.

Assessment: Argument layering is pragmatic.

## Config File Loading

Config files are loaded by Config.from_pyproject() in both subcommand handlers. Config values are merged with CLI flag overrides via a three-level hierarchy:
1. CLI flag (highest priority)
2. Config file value
3. Default value (lowest priority)

Assessment: Config layering is intuitive and follows standard conventions.

## Output Formatting

Linter supports two output formats:
- plain: Text format (file:line: RULE message)
- github: GitHub Actions annotation format (::error file=X,line=Y::message)

Violations are formatted via Violation.format_text() or format_github().

Assessment: Dual format support is necessary for GitHub Actions integration and local debugging.

## Error Handling

Return codes: 0 for success, non-zero for failure (including linting errors found).

Assessment: Standard and correct.

## Conclusion

The CLI is well-designed. Subcommand dispatch via string check is pragmatic. Config layering is clear. Dual output formats support both CI and local use.

No significant code quality issues identified.
