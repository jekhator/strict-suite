"""Tests for R002: Inline dict literals with 3+ string keys."""

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestR002InlineDict:
    """Test suite for related functionality."""

    def test_r002_good_few_keys(self, fixture_dir):
        """Good: dict literals with <3 keys."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "good" / "r002_good_dict.py")
        r002_violations = [v for v in violations if v.rule_id == "R002"]
        assert len(r002_violations) == 0

    def test_r002_bad_inline_dict(self, fixture_dir):
        """Bad: inline dict literals with 3+ keys."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r002_bad_inline.py")
        r002_violations = [v for v in violations if v.rule_id == "R002"]
        assert len(r002_violations) >= 1
