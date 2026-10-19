"""Main linter implementation."""

import ast
import hashlib
import json
from pathlib import Path

from strict_checkers import (
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
    R012Checker,
    R013Checker,
    R014Checker,
    R015Checker,
)
from strict_checkers.base import BaseChecker
from strict_config._config import Config
from strict_config.constants import (
    ERR_BASELINE_ENTRY_NOT_OBJECT,
    ERR_BASELINE_ENTRY_SHAPE,
    ERR_BASELINE_INVALID_JSON,
    ERR_BASELINE_MISSING,
    ERR_BASELINE_NOT_LIST,
    EXIT_CODE_HIGH_VIOLATION,
    EXIT_CODE_LOW_VIOLATION,
    EXIT_CODE_MEDIUM_VIOLATION,
    EXIT_CODE_SUCCESS,
    FORMAT_GITHUB,
    FORMAT_JSON,
    FORMAT_TEXT,
    PY_EXTENSION,
    REQUIRED_BASELINE_KEYS,
    VALID_SEVERITY_LEVELS,
)
from strict_linter.linter_objects import BaselineLoadError
from strict_rules import RuleSeverity, Violation

CHECKER_CLASSES: tuple[type[BaseChecker], ...] = (
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
    R012Checker,
    R013Checker,
    R014Checker,
    R015Checker,
)

EXIT_CODE_BY_SEVERITY: dict[RuleSeverity, int] = {
    RuleSeverity.HIGH: EXIT_CODE_HIGH_VIOLATION,
    RuleSeverity.MEDIUM: EXIT_CODE_MEDIUM_VIOLATION,
    RuleSeverity.LOW: EXIT_CODE_LOW_VIOLATION,
}


class DtoStrictLinter:
    """AST-based linter for DTO discipline."""

    def __init__(
        self,
        config: Config,
        baseline: dict[tuple[str, int, str], str] | None = None,
    ):
        self.config = config
        self.baseline = baseline or {}

    def lint_file(self, file_path: Path) -> list[Violation]:
        """Lint a single Python file."""
        if file_path.suffix != PY_EXTENSION:
            return []

        try:
            source = file_path.read_text()
        except Exception:
            return []

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        violations: list[Violation] = []
        for checker_cls in CHECKER_CLASSES:
            checker = checker_cls(file_path, source, self.config)
            checker.visit(tree)
            violations.extend(checker.violations)

        return self._filter(violations)

    def lint_path(self, path: Path) -> list[Violation]:
        """Lint all Python files in a directory or single file."""
        all_violations: list[Violation] = []

        if path.is_file():
            all_violations.extend(self.lint_file(path))
        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                all_violations.extend(self.lint_file(py_file))

        return [self._apply_severity_override(v) for v in all_violations]

    def _filter(self, violations: list[Violation]) -> list[Violation]:
        """Drop violations of disabled rules and violations accepted by the baseline."""
        enabled = [v for v in violations if self.config.is_rule_enabled(v.rule_id)]
        if self.baseline:
            return self._filter_by_baseline(enabled)
        return enabled

    def _apply_severity_override(self, violation: Violation) -> Violation:
        """Return the violation with the configured severity when the override is valid."""
        override = self.config.severity_overrides.get(violation.rule_id)
        if override is None:
            return violation

        new_severity = override.upper()
        if new_severity not in VALID_SEVERITY_LEVELS:
            return violation

        return Violation(
            rule_id=violation.rule_id,
            severity=RuleSeverity[new_severity],
            file=violation.file,
            line=violation.line,
            col=violation.col,
            message=violation.message,
        )

    def _filter_by_baseline(self, violations: list[Violation]) -> list[Violation]:
        """Filter violations by baseline, removing accepted violations by file+line+rule_id."""
        return [
            v for v in violations if (v.file, v.line, v.rule_id) not in self.baseline
        ]

    @staticmethod
    def _hash_message(message: str) -> str:
        """Hash violation message for baseline comparison."""
        return hashlib.sha256(message.encode()).hexdigest()[:16]

    def generate_baseline(
        self, violations: list[Violation]
    ) -> list[dict[str, str | int]]:
        """Generate baseline JSON from violations."""
        return [
            {
                "file": v.file,
                "line": v.line,
                "rule_id": v.rule_id,
                "message_hash": self._hash_message(v.message),
            }
            for v in violations
        ]

    @staticmethod
    def load_baseline(baseline_path: Path) -> dict[tuple[str, int, str], str]:
        """Load baseline JSON file."""
        try:
            with open(baseline_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise BaselineLoadError(
                ERR_BASELINE_INVALID_JSON.format(path=baseline_path)
            ) from error
        except OSError as error:
            raise BaselineLoadError(
                ERR_BASELINE_MISSING.format(path=baseline_path)
            ) from error

        if not isinstance(data, list):
            raise BaselineLoadError(ERR_BASELINE_NOT_LIST.format(path=baseline_path))

        baseline: dict[tuple[str, int, str], str] = {}
        for index, entry in enumerate(data):
            if not isinstance(entry, dict):
                raise BaselineLoadError(
                    ERR_BASELINE_ENTRY_NOT_OBJECT.format(
                        index=index, path=baseline_path
                    )
                )
            for key in REQUIRED_BASELINE_KEYS:
                if key not in entry:
                    raise BaselineLoadError(
                        ERR_BASELINE_ENTRY_SHAPE.format(
                            index=index, key=key, path=baseline_path
                        )
                    )
            baseline_key = (entry["file"], entry["line"], entry["rule_id"])
            baseline[baseline_key] = entry["message_hash"]
        return baseline

    def format_violations(
        self, violations: list[Violation], format_type: str = FORMAT_TEXT
    ) -> str:
        """Format violations for output."""
        if format_type == FORMAT_GITHUB:
            return "\n".join(v.format_github() for v in violations)
        if format_type == FORMAT_JSON:
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
        return "\n".join(v.format_text() for v in violations)

    @staticmethod
    def get_exit_code(violations: list[Violation]) -> int:
        """Determine exit code from the most severe blocking violation (INFO never blocks)."""
        severities = {v.severity for v in violations}
        for severity, exit_code in EXIT_CODE_BY_SEVERITY.items():
            if severity in severities:
                return exit_code
        return EXIT_CODE_SUCCESS
