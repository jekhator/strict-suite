"""Command-line interface for strict-module (formerly dto-strict)."""

import argparse
import json
import sys
from pathlib import Path

from strict_config._config import Config, ConfigLoadError
from strict_config.constants import (
    DEFAULT_LOC_CAP_BASELINE_FILE,
    DEFAULT_LOC_HARD_CAP,
    DEFAULT_LOC_SOFT_TARGET,
    ERR_NONEXISTENT_PATH,
    EXIT_CODE_HIGH_VIOLATION,
    EXIT_CODE_SUCCESS,
    FORMAT_TEXT,
    MSG_BASELINE_LOADED,
    VALID_FORMATS,
)
from strict_linter import BaselineLoadError, DtoStrictLinter, LintInputError
from strict_loc_cap import LocCap
from strict_rules import Violation

LOC_CAP_SUBCOMMAND = "loc-cap"


def _add_config_option(  # module-level: stateless helper
    parser: argparse.ArgumentParser,
) -> None:
    """Add the --config option shared by the linter and loc-cap parsers."""
    parser.add_argument(
        "--config",
        default="pyproject.toml",
        help="Path to pyproject.toml config file (default: pyproject.toml)",
    )


def _add_generate_baseline_option(  # module-level: stateless helper
    parser: argparse.ArgumentParser, help_text: str
) -> None:
    """Add the --generate-baseline flag with a subcommand-specific help text."""
    parser.add_argument("--generate-baseline", action="store_true", help=help_text)


def _lint_all(  # module-level: stateless helper
    linter: DtoStrictLinter, path_strs: list[str]
) -> list[Violation] | None:
    """Lint every path; print an unreadable or unparseable input to stderr and return None."""
    violations: list[Violation] = []
    try:
        for path_str in path_strs:
            violations.extend(linter.lint_path(Path(path_str)))
    except LintInputError as error:
        print(str(error), file=sys.stderr)
        return None
    return violations


def _load_config(config_path: str) -> Config | None:  # module-level: stateless helper
    """Load configuration, printing the error to stderr and returning None when it is invalid."""
    try:
        return Config.from_pyproject(Path(config_path))
    except ConfigLoadError as error:
        print(str(error), file=sys.stderr)
        return None


def handle_loc_cap(args: list[str]) -> int:
    """Handle loc-cap subcommand (invoked when sys.argv[1] == 'loc-cap')."""
    parser = argparse.ArgumentParser(
        prog="dto-strict loc-cap",
        description="LOC cap enforcer with configurable hard/soft limits and ratchet baseline.",
    )
    parser.add_argument("path", help="Path to directory to scan")
    _add_config_option(parser)
    parser.add_argument(
        "--hard-cap",
        type=int,
        help=f"Hard cap limit (default: {DEFAULT_LOC_HARD_CAP}, or from [tool.strict-module.loc-cap].hard_cap)",
    )
    parser.add_argument(
        "--soft-target",
        type=int,
        help=f"Soft target limit (default: {DEFAULT_LOC_SOFT_TARGET}, or from [tool.strict-module.loc-cap].soft_target)",
    )
    parser.add_argument(
        "--baseline",
        help=f"Baseline file path (default: {DEFAULT_LOC_CAP_BASELINE_FILE}, or from [tool.strict-module.loc-cap].baseline_file)",
    )
    _add_generate_baseline_option(
        parser, "Generate baseline from all Python files in path (stdout)"
    )

    parsed = parser.parse_args(args[2:])

    config = _load_config(parsed.config)
    if config is None:
        return EXIT_CODE_HIGH_VIOLATION

    hard_cap = (
        parsed.hard_cap if parsed.hard_cap is not None else config.loc_cap.hard_cap
    )
    soft_target = (
        parsed.soft_target
        if parsed.soft_target is not None
        else config.loc_cap.soft_target
    )
    baseline_file = parsed.baseline if parsed.baseline else config.loc_cap.baseline_file

    return LocCap.run_loc_cap(
        path=parsed.path,
        hard_cap=hard_cap,
        soft_target=soft_target,
        baseline_file=baseline_file,
        generate=parsed.generate_baseline,
    )


def main() -> int:
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == LOC_CAP_SUBCOMMAND:
        return handle_loc_cap(sys.argv)

    parser = argparse.ArgumentParser(
        description="AST-based linter for Python DTO discipline and facade-ban enforcement."
    )
    parser.add_argument("path", nargs="*", help="Path(s) to file or directory to lint")
    _add_config_option(parser)
    parser.add_argument(
        "--format",
        choices=VALID_FORMATS,
        default=FORMAT_TEXT,
        help=f"Output format (default: {FORMAT_TEXT})",
    )
    _add_generate_baseline_option(
        parser,
        "Generate baseline JSON from all violations in path and output to stdout",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Path to baseline JSON file; violations in baseline are accepted (ratchet mode)",
    )

    args = parser.parse_args()

    config = _load_config(args.config)
    if config is None:
        return EXIT_CODE_HIGH_VIOLATION

    linter = DtoStrictLinter(config)

    if args.generate_baseline:
        if not args.path:
            print("error: --generate-baseline requires PATH argument", file=sys.stderr)
            return EXIT_CODE_HIGH_VIOLATION

        generation_violations = _lint_all(linter, args.path)
        if generation_violations is None:
            return EXIT_CODE_HIGH_VIOLATION

        baseline_data = linter.generate_baseline(generation_violations)
        print(json.dumps(baseline_data, indent=2))
        return EXIT_CODE_SUCCESS

    if not args.path:
        print(
            "error: PATH argument required (unless using --generate-baseline)",
            file=sys.stderr,
        )
        return EXIT_CODE_HIGH_VIOLATION

    for path_str in args.path:
        if not Path(path_str).exists():
            print(ERR_NONEXISTENT_PATH.format(path=path_str), file=sys.stderr)
            return EXIT_CODE_HIGH_VIOLATION

    if args.baseline:
        try:
            baseline = DtoStrictLinter.load_baseline(args.baseline)
        except BaselineLoadError as error:
            print(str(error), file=sys.stderr)
            return EXIT_CODE_HIGH_VIOLATION
        print(
            MSG_BASELINE_LOADED.format(count=len(baseline), path=args.baseline),
            file=sys.stderr,
        )
        linter = DtoStrictLinter(config, baseline=baseline)

    all_violations = _lint_all(linter, args.path)
    if all_violations is None:
        return EXIT_CODE_HIGH_VIOLATION

    if all_violations:
        print(linter.format_violations(all_violations, args.format))

    return linter.get_exit_code(all_violations)


if __name__ == "__main__":
    sys.exit(main())
