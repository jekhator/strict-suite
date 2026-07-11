"""Tests for R008: bare module-level test functions."""

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestR008TestFunctions:
    """Test suite for related functionality."""

    def test_r008_bad_bare_test_functions(self, fixture_dir):
        """Bad: test functions defined at module level."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "bad" / "test_r008_bad_bare_test_functions.py"
        )
        r008_violations = [v for v in violations if v.rule_id == "R008"]
        # Should find at least 3 bare test functions
        assert len(r008_violations) >= 3
        assert all("module-level" in v.message.lower() for v in r008_violations)
        assert any("test_addition" in v.message for v in r008_violations)

    def test_r008_good_test_functions_in_classes(self, fixture_dir):
        """Good: test functions properly organized in classes."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "good" / "test_r008_good_test_class.py")
        r008_violations = [v for v in violations if v.rule_id == "R008"]
        assert len(r008_violations) == 0
