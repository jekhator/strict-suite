"""Tests for R004: module-level facades around class methods."""

from strict_config import constants as const
from strict_config._config import Config
from strict_linter import DtoStrictLinter
from strict_rules import RuleSeverity


class TestR004ModuleFacade:
    """Test suite for R004 facade detection in service paths."""

    def test_r004_good_fixture_has_no_facades(self, fixture_dir):
        """Tagged wrappers, docstring-tagged wrappers, and real helpers are not facades."""
        config = Config(service_paths=["**/*.py"])
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "good" / "r004_good_facade.py")
        r004_violations = [v for v in violations if v.rule_id == "R004"]

        assert r004_violations == []

    def test_r004_bad_fixture_flags_every_facade_shape(self, fixture_dir):
        """Each delegation shape (direct, new instance, named instance, bare expression) is flagged."""
        config = Config(service_paths=["**/*.py"])
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r004_bad_facade.py")
        r004_violations = [v for v in violations if v.rule_id == "R004"]

        assert len(r004_violations) == 4, (
            f"Expected 4 facade violations, got {len(r004_violations)}: {r004_violations}"
        )
        assert all(v.severity == RuleSeverity.HIGH for v in r004_violations)

    def test_r004_message_names_the_class_method(self, fixture_dir):
        """The facade message names the wrapped class and method."""
        config = Config(service_paths=["**/*.py"])
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r004_bad_facade.py")
        messages = [v.message for v in violations if v.rule_id == "R004"]

        assert any("Facade 'get_user': module-level wrapper around UserService.get_user" in m for m in messages)
        assert any("'# FRAMEWORK'" in m for m in messages)

    def test_r004_only_applies_to_service_paths(self, fixture_dir):
        """Outside service paths R004 is silent even for a facade shape."""
        config = Config(service_paths=["apps/*/services/*.py"])
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r004_bad_facade.py")

        assert [v for v in violations if v.rule_id == "R004"] == []

    def test_r004_ignores_untagged_helper_with_logic(self, fixture_dir):
        """An untagged module-level helper with real logic is R009 advice, not R004."""
        config = Config(service_paths=["**/*.py"])
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "good" / "r004_good_facade.py")
        r009_violations = [v for v in violations if v.rule_id == "R009"]

        assert len(r009_violations) == 1
        assert r009_violations[0].severity == RuleSeverity.INFO

    def test_r004_default_exception_tags_include_framework(self):
        """The framework tag remains a default exception tag."""
        assert const.TAG_FRAMEWORK in Config().exception_tags
