"""Command-line interface for strict-module (formerly dto-strict)."""

import argparse
import json
import sys
from pathlib import Path

from .config import Config
from .linter import DtoStrictLinter
from .loc_cap import run_loc_cap


def handle_loc_cap(args: list[str]) -> int:
    """Handle loc-cap subcommand (invoked when sys.argv[1] == 'loc-cap')."""
    parser = argparse.ArgumentParser(
        prog="dto-strict loc-cap",
        description="LOC cap enforcer with configurable hard/soft limits and ratchet baseline.",
    )
    parser.add_argument("path", help="Path to directory to scan")
    parser.add_argument(
        "--config",
        default="pyproject.toml",
        help="Path to pyproject.toml config file (default: pyproject.toml)",
    )
    parser.add_argument(
        "--hard-cap",
        type=int,
        help="Hard cap limit (default: 694, or from [tool.strict-module.loc-cap].hard_cap)",
    )
    parser.add_argument(
        "--soft-target",
        type=int,
        help="Soft target limit (default: 500, or from [tool.strict-module.loc-cap].soft_target)",
    )
    parser.add_argument(
        "--baseline",
        help="Baseline file path (default: .loc-cap-baseline.txt, or from [tool.strict-module.loc-cap].baseline_file)",
    )
    parser.add_argument(
        "--generate-baseline",
        action="store_true",
        help="Generate baseline from all Python files in path (stdout)",
    )

    parsed = parser.parse_args(args[2:])  # Skip 'dto-strict' and 'loc-cap'

    # Load config from pyproject
    config_path = Path(parsed.config)
    config = Config.from_pyproject(config_path)

    # Determine final values: CLI flag > config file > default
    hard_cap = (
        parsed.hard_cap if parsed.hard_cap is not None else config.loc_cap.hard_cap
    )
    soft_target = (
        parsed.soft_target
        if parsed.soft_target is not None
        else config.loc_cap.soft_target
    )
    baseline_file = parsed.baseline if parsed.baseline else config.loc_cap.baseline_file

    # Run loc-cap checker
    return run_loc_cap(
        path=parsed.path,
        hard_cap=hard_cap,
        soft_target=soft_target,
        baseline_file=baseline_file,
        generate=parsed.generate_baseline,
    )


def main() -> int:
    """Main CLI entry point."""
    # Check for loc-cap subcommand (dispatch before argparse)
    if len(sys.argv) > 1 and sys.argv[1] == "loc-cap":
        return handle_loc_cap(sys.argv)

    parser = argparse.ArgumentParser(
        description="AST-based linter for Python DTO discipline and facade-ban enforcement."
    )
    parser.add_argument("path", nargs="*", help="Path(s) to file or directory to lint")
    parser.add_argument(
        "--config",
        default="pyproject.toml",
        help="Path to pyproject.toml config file (default: pyproject.toml)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "github", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--generate-baseline",
        action="store_true",
        help="Generate baseline JSON from all violations in path and output to stdout",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Path to baseline JSON file; violations in baseline are accepted (ratchet mode)",
    )

    args = parser.parse_args()

    # Load configuration
    config_path = Path(args.config)
    config = Config.from_pyproject(config_path)

    # If generating baseline, require path
    if args.generate_baseline:
        if not args.path:
            print("error: --generate-baseline requires PATH argument", file=sys.stderr)
            return 1

        # Lint all provided paths for baseline generation
        all_violations = []
        for path_str in args.path:
            target_path = Path(path_str)
            linter = DtoStrictLinter(config)
            all_violations.extend(linter.lint_path(target_path))

        baseline_data = linter.generate_baseline(all_violations)
        print(json.dumps(baseline_data, indent=2))
        return 0

    # Normal linting mode
    if not args.path:
        print(
            "error: PATH argument required (unless using --generate-baseline)",
            file=sys.stderr,
        )
        return 1

    # Load baseline if provided
    baseline = None
    if args.baseline:
        baseline = DtoStrictLinter.load_baseline(args.baseline)

    # Lint all provided paths
    linter = DtoStrictLinter(config, baseline=baseline)
    all_violations = []
    for path_str in args.path:
        target_path = Path(path_str)
        all_violations.extend(linter.lint_path(target_path))

    # Output results
    if all_violations:
        output = linter.format_violations(all_violations, args.format)
        print(output)

    # Return exit code
    return linter.get_exit_code(all_violations)


if __name__ == "__main__":
    sys.exit(main())
