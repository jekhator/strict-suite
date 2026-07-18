"""Main linter implementation."""

import ast
import hashlib
import json
from pathlib import Path

from strict_module.checkers import (
    R001Checker,
    R002Checker,
    R003Checker,
    R004Checker,
    R005Checker,
    R006Checker,
    R007Checker,
    R008Checker,
    R009Checker,
    R010Checker,
    R011Checker,
)
from strict_module.config import Config
from strict_module.constants import (
    EXIT_CODE_HIGH_VIOLATION,
    EXIT_CODE_LOW_VIOLATION,
    EXIT_CODE_MEDIUM_VIOLATION,
    EXIT_CODE_SUCCESS,
    FORMAT_GITHUB,
    FORMAT_JSON,
    FORMAT_TEXT,
    PY_EXTENSION,
    VALID_SEVERITY_LEVELS,
)
from strict_module.rules import RuleSeverity, Violation


class DtoStrictLinter:
    """AST-based linter for DTO discipline."""

    def __init__(
        self, config: Config, baseline: dict[tuple[str, int, str], str] | None = None
    ):
        self.config = config
        self.violations: list[Violation] = []
        self.baseline = baseline or {}

    def lint_file(self, file_path: Path) -> list[Violation]:
        """Lint a single Python file."""
        if not file_path.suffix == PY_EXTENSION:
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

        for checker_cls in [
            R001Checker,
            R002Checker,
            R003Checker,
            R004Checker,
            R005Checker,
            R006Checker,
            R007Checker,
            R008Checker,
            R009Checker,
            R010Checker,
            R011Checker,
        ]:
            checker = checker_cls(file_path, source, self.config)
            checker.visit(tree)
            violations.extend(checker.violations)

        filtered = []
        for v in violations:
            if self.config.is_rule_enabled(v.rule_id):
                filtered.append(v)

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

        filtered = []
        for v in all_violations:
            if self.config.is_rule_enabled(v.rule_id):
                filtered.append(v)

        if self.baseline:
            filtered = self._filter_by_baseline(filtered)

        overridden = []
        for violation in filtered:
            if violation.rule_id in self.config.severity_overrides:
                new_severity = self.config.severity_overrides[violation.rule_id].upper()
                if new_severity in VALID_SEVERITY_LEVELS:
                    violation = Violation(
                        rule_id=violation.rule_id,
                        severity=RuleSeverity[new_severity],
                        file=violation.file,
                        line=violation.line,
                        col=violation.col,
                        message=violation.message,
                    )
            overridden.append(violation)

        return overridden

    def _filter_by_baseline(self, violations: list[Violation]) -> list[Violation]:
        """Filter violations by baseline, removing accepted violations by file+line+rule_id."""
        new_violations = []
        for v in violations:
            key = (v.file, v.line, v.rule_id)
            if key not in self.baseline:
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
        self, violations: list[Violation], format_type: str = FORMAT_TEXT
    ) -> str:
        """Format violations for output."""
        if format_type == FORMAT_GITHUB:
            return "\n".join(v.format_github() for v in violations)
        elif format_type == FORMAT_JSON:
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
        else:
            return "\n".join(v.format_text() for v in violations)

    def get_exit_code(self, violations: list[Violation]) -> int:
        """Determine exit code based on violation severities."""
        if not violations:
            return EXIT_CODE_SUCCESS

        has_high = any(v.severity == RuleSeverity.HIGH for v in violations)
        has_medium = any(v.severity == RuleSeverity.MEDIUM for v in violations)
        has_low = any(v.severity == RuleSeverity.LOW for v in violations)
        has_info = any(v.severity == RuleSeverity.INFO for v in violations)

        if has_high:
            return EXIT_CODE_HIGH_VIOLATION
        elif has_medium:
            return EXIT_CODE_MEDIUM_VIOLATION
        elif has_low:
            return EXIT_CODE_LOW_VIOLATION
        elif has_info:
            return EXIT_CODE_SUCCESS
        else:
            return EXIT_CODE_SUCCESS
