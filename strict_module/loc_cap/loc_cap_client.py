"""LOC cap enforcer for Python codebases with ratchet baseline semantics."""

import os
from pathlib import Path

from strict_module.constants import (
    DEFAULT_EXCLUDE_PATTERNS,
    DEFAULT_LOC_CAP_BASELINE_FILE,
    DEFAULT_LOC_HARD_CAP,
    DEFAULT_LOC_SOFT_TARGET,
    EXIT_CODE_HIGH_VIOLATION,
    EXIT_CODE_SUCCESS,
    LOC_CAP_BASELINE_LEGACY_NAMES,
    PY_EXTENSION,
)
from strict_module.inspection import PathClassifier


class LocCap:
    """LOC cap enforcer with configurable hard/soft limits and baseline ratchet."""

    @staticmethod
    def count_lines(file_path: str) -> int:
        """Count all lines (matches wc -l semantics for baseline compatibility)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except (OSError, UnicodeDecodeError):
            return 0

    @staticmethod
    def load_baseline(baseline_file: str) -> dict[str, int]:
        """Load baseline LOC counts from file (with fallback for backward compatibility)."""
        baseline: dict[str, int] = {}

        actual_file = None
        if os.path.isfile(baseline_file):
            actual_file = baseline_file
        elif baseline_file == DEFAULT_LOC_CAP_BASELINE_FILE:
            for fallback in LOC_CAP_BASELINE_LEGACY_NAMES:
                if os.path.isfile(fallback):
                    actual_file = fallback
                    break

        if not actual_file:
            return baseline

        try:
            with open(actual_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.rsplit(":", 1)
                    if len(parts) == 2:
                        path, loc_str = parts
                        try:
                            baseline[path.strip()] = int(loc_str.strip())
                        except ValueError:
                            continue
        except OSError:
            pass

        return baseline

    @staticmethod
    def find_python_files(
        root_path: str,
        exclude_patterns: tuple[str, ...] = DEFAULT_EXCLUDE_PATTERNS,
    ) -> dict[str, int]:
        """Find all Python files under root_path, exempting test files and excluded patterns."""
        current_locs: dict[str, int] = {}
        root = Path(root_path).resolve()

        if not root.exists():
            return current_locs

        for file_path in root.rglob(f"*{PY_EXTENSION}"):
            file_str = str(file_path)
            if any(excl in file_str for excl in exclude_patterns):
                continue

            if PathClassifier.is_loc_test_file(file_path):
                continue

            loc = LocCap.count_lines(file_str)
            current_locs[file_str] = loc

        return current_locs

    @staticmethod
    def generate_baseline(
        root_path: str,
        exclude_patterns: tuple[str, ...] = DEFAULT_EXCLUDE_PATTERNS,
        floor: int = 0,
    ) -> str:
        """Generate baseline output in path:loc format, sorted by LOC descending."""
        files = LocCap.find_python_files(root_path, exclude_patterns)

        filtered = [(path, loc) for path, loc in files.items() if loc >= floor]
        sorted_files = sorted(filtered, key=lambda x: (-x[1], x[0]))

        lines = [f"{path}:{loc}" for path, loc in sorted_files]
        return "\n".join(lines)

    @staticmethod
    def run_loc_cap(
        path: str,
        hard_cap: int = DEFAULT_LOC_HARD_CAP,
        soft_target: int = DEFAULT_LOC_SOFT_TARGET,
        baseline_file: str = DEFAULT_LOC_CAP_BASELINE_FILE,
        exclude_patterns: tuple[str, ...] = DEFAULT_EXCLUDE_PATTERNS,
        generate: bool = False,
    ) -> int:
        """Run LOC cap checker with hard/soft caps and baseline ratchet enforcement."""
        if generate:
            baseline_output = LocCap.generate_baseline(path, exclude_patterns, floor=0)
            print(baseline_output)
            return EXIT_CODE_SUCCESS

        baseline = LocCap.load_baseline(baseline_file)
        current = LocCap.find_python_files(path, exclude_patterns)

        soft_warnings = []
        hard_violations = []
        improvements = []

        for path_str, loc in current.items():
            if soft_target < loc <= hard_cap:
                soft_warnings.append(f"  {loc}  {path_str}")

            if loc > hard_cap:
                if path_str not in baseline:
                    hard_violations.append(f"  {loc}  {path_str} (NEW OFFENDER)")
                elif loc > baseline[path_str]:
                    delta = loc - baseline[path_str]
                    hard_violations.append(
                        f"  {loc}  {path_str} (was {baseline[path_str]}, grew by {delta})"
                    )

        for baseline_path, baseline_loc in baseline.items():
            current_loc = current.get(baseline_path)

            if current_loc is None:
                improvements.append(f"  {baseline_path} (deleted)")
            elif current_loc < baseline_loc:
                if current_loc <= hard_cap:
                    delta = baseline_loc - current_loc
                    improvements.append(
                        f"  {current_loc}  {baseline_path} (was {baseline_loc}, improved by {delta})"
                    )

        if soft_warnings:
            print(
                f"::warning::Files over soft target ({soft_target} LOC) - consider decomposition:"
            )
            print("\n".join(soft_warnings))
            print()

        if improvements:
            print(f"::notice::Files improved (under {hard_cap} LOC):")
            print("\n".join(improvements))
            print()

        if hard_violations:
            print(
                f"::error::Files exceed hard cap of {hard_cap} LOC. Decompose by cohesion:"
            )
            print("\n".join(hard_violations))
            print()
            print(
                "See memory/feedback_dto_refactor_autonomous_priority.md for cap rationale."
            )
            print(
                "Tests: cap applies. Decompose by class-under-test; lift fixtures to conftest if needed."
            )
            print(
                "Refactor approach: split by COHESION not line count. E.g., bedrock.py -> bedrock/{invoke,embed,dtos}.py"
            )
            return EXIT_CODE_HIGH_VIOLATION

        print(
            f"✓ All Python files within {hard_cap} LOC cap (ratchet: baseline allows improvements)"
        )
        return EXIT_CODE_SUCCESS
