"""Tests for R010: Legacy typing aliases for abstract base classes."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR010LegacyTypingABC:
    """Test suite for R010 legacy typing ABC detection."""

    def test_r010_detects_legacy_typing_imports(self, fixture_dir):
        """R010 should flag imports of typing.* ABCs."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r010_legacy_typing_abc.py")
        r010_violations = [v for v in violations if v.rule_id == "R010"]

        assert len(r010_violations) == 4, (
            f"Expected 4 R010 violations (Callable, Mapping, Iterable, Awaitable), "
            f"got {len(r010_violations)}"
        )

    def test_r010_allows_collections_abc_imports(self, fixture_dir):
        """R010 should not flag collections.abc imports."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "good" / "r010_modern_abc_imports.py"
        )
        r010_violations = [v for v in violations if v.rule_id == "R010"]

        assert len(r010_violations) == 0, (
            f"Expected 0 R010 violations for collections.abc imports, "
            f"got {len(r010_violations)}"
        )

    def test_r010_allows_typing_non_abc_imports(self, fixture_dir):
        """R010 should allow typing imports that are not ABCs (Any, TypeVar, etc.)."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "good" / "r010_modern_abc_imports.py"
        )
        r010_violations = [v for v in violations if v.rule_id == "R010"]

        assert len(r010_violations) == 0, (
            "R010 should not flag typing.Any, typing.TypeVar, etc."
        )

    def test_r010_message_suggests_collections_abc(self, fixture_dir):
        """R010 violation message should suggest using collections.abc."""
        config = Config(
            service_paths=["**/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
            disabled_rules=[],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r010_legacy_typing_abc.py")
        r010_violations = [v for v in violations if v.rule_id == "R010"]

        assert len(r010_violations) > 0
        message = r010_violations[0].message
        assert "collections.abc" in message, "Message should suggest collections.abc"
