"""Main linter implementation."""

import ast
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass

from .checkers import (
    R001Checker,
    R002Checker,
    R003Checker,
    R004Checker,
    R005Checker,
    R006Checker,
    R007Checker,
    R008Checker,
)
from .config import Config
from .rules import RuleSeverity, Violation


@dataclass(frozen=True, slots=True)
class BaselineEntry:
    """Baseline entry for tracking accepted violations."""

    file: str
    line: int
    rule_id: str
    message_hash: str


class DtoStrictLinter:
    """AST-based linter for DTO discipline."""

    def __init__(
        self, config: Config, baseline: dict[tuple[str, int, str], str] | None = None
    ):
        self.config = config
        self.violations: list[Violation] = []
        self.baseline = (
            baseline or {}
        )  # Key: (file, line, rule_id), Value: message_hash

    def lint_file(self, file_path: Path) -> list[Violation]:
        """Lint a single Python file."""
        if not file_path.suffix == ".py":
            return []

        try:
            source = file_path.read_text()
        except Exception:
            return []

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        violations = []

        # Run all checkers
        for checker_cls in [
            R001Checker,
            R002Checker,
            R003Checker,
            R004Checker,
            R005Checker,
            R006Checker,
            R007Checker,
            R008Checker,
        ]:
            checker = checker_cls(file_path, source, self.config)
            checker.visit(tree)
            violations.extend(checker.violations)

        # Filter by enabled rules
        filtered = []
        for v in violations:
            if self.config.is_rule_enabled(v.rule_id):
                filtered.append(v)

        # Apply baseline filtering if present
        if self.baseline:
            filtered = self._filter_by_baseline(filtered)

        return filtered

    def lint_path(self, path: Path) -> list[Violation]:
        """Lint all Python files in a directory or single file."""
        all_violations = []

        if path.is_file():
            all_violations.extend(self.lint_file(path))
        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                all_violations.extend(self.lint_file(py_file))

        # Filter by enabled rules
        filtered = []
        for v in all_violations:
            if self.config.is_rule_enabled(v.rule_id):  # pragma: no cover
                filtered.append(v)

        # Apply baseline filtering if present
        if self.baseline:  # pragma: no cover
            filtered = self._filter_by_baseline(filtered)

        # Apply severity overrides
        for violation in filtered:
            if violation.rule_id in self.config.severity_overrides:  # pragma: no cover
                new_severity = self.config.severity_overrides[violation.rule_id].upper()
                if new_severity in ["HIGH", "MEDIUM", "LOW"]:  # pragma: no cover
                    violation = Violation(
                        rule_id=violation.rule_id,
                        severity=RuleSeverity[new_severity],
                        file=violation.file,
                        line=violation.line,
                        col=violation.col,
                        message=violation.message,
                    )

        return filtered

    def _filter_by_baseline(self, violations: list[Violation]) -> list[Violation]:
        """Filter violations by baseline, removing accepted violations by file+line+rule_id."""
        new_violations = []
        for v in violations:
            key = (v.file, v.line, v.rule_id)
            if key not in self.baseline:
                # New violation not in baseline
                new_violations.append(v)
        return new_violations

    @staticmethod
    def _hash_message(message: str) -> str:
        """Hash violation message for baseline comparison."""
        return hashlib.sha256(message.encode()).hexdigest()[:16]

    def generate_baseline(self, violations: list[Violation]) -> list[dict]:
        """Generate baseline JSON from violations."""
        baseline_data = []
        for v in violations:
            baseline_data.append(
                {
                    "file": v.file,
                    "line": v.line,
                    "rule_id": v.rule_id,
                    "message_hash": self._hash_message(v.message),
                }
            )
        return baseline_data

    @staticmethod
    def load_baseline(baseline_path: Path) -> dict[tuple[str, int, str], str]:
        """Load baseline JSON file."""
        try:
            with open(baseline_path, "r") as f:
                data = json.load(f)
            baseline = {}
            for entry in data:
                key = (entry["file"], entry["line"], entry["rule_id"])
                baseline[key] = entry["message_hash"]
            return baseline
        except Exception:
            return {}

    def format_violations(
        self, violations: list[Violation], format_type: str = "text"
    ) -> str:
        """Format violations for output."""
        if format_type == "github":
            return "\n".join(v.format_github() for v in violations)
        elif format_type == "json":
            import json

            return json.dumps(
                [
                    {
                        "rule_id": v.rule_id,
                        "severity": v.severity.value,
                        "file": v.file,
                        "line": v.line,
                        "col": v.col,
                        "message": v.message,
                    }
                    for v in violations
                ],
                indent=2,
            )
        else:  # text
            return "\n".join(v.format_text() for v in violations)

    def get_exit_code(self, violations: list[Violation]) -> int:
        """Determine exit code based on violation severities."""
        if not violations:
            return 0

        has_high = any(v.severity == RuleSeverity.HIGH for v in violations)
        has_medium = any(v.severity == RuleSeverity.MEDIUM for v in violations)

        if has_high:
            return 1
        elif has_medium:
            return 2
        else:
            return 3
