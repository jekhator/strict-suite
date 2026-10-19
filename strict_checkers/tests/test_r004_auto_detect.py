"""Tests for R004 facade detection on module-level delegation patterns."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from strict_config._config import Config
from strict_linter import DtoStrictLinter
from strict_rules import RuleSeverity


def _lint_source(source: str, config: Config) -> list:
    """Write source to a temporary file and lint it, returning the violations."""
    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as handle:
        handle.write(source)
        handle.flush()
        path = Path(handle.name)

    try:
        return DtoStrictLinter(config).lint_file(path)
    finally:
        path.unlink()


class TestR004AutoDetect:
    """Test suite for facade detection through instance and class references."""

    def test_r004_instance_wrapper_is_not_a_facade(self):
        """A lowercase instance reference is not a class reference, so no facade is reported."""
        config = Config(service_paths=["**/*.py"])
        source = """
class UserService:
    @staticmethod
    def get_user(user_id: int):
        return user_id

_service = UserService()

def get_user_wrapper(user_id: int):
    return _service.get_user(user_id)
"""
        violations = _lint_source(source, config)
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert r004_violations == []

    def test_r004_class_reference_wrapper_is_a_facade(self):
        """Calling a class method through the class name is a facade."""
        config = Config(service_paths=["**/*.py"])
        source = """
class UserService:
    @staticmethod
    def get_user(user_id: int):
        return user_id

def another_wrapper(user_id: int):
    return UserService.get_user(user_id)
"""
        violations = _lint_source(source, config)
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert len(r004_violations) == 1
        assert "another_wrapper" in r004_violations[0].message

    def test_r004_untagged_function_with_logic_is_not_r004(self):
        """An untagged function with logic is R009 advice, never a blocking R004 finding."""
        config = Config(service_paths=["**/*.py"])
        source = """
def pure_utility(x: int):
    return x * 2
"""
        violations = _lint_source(source, config)
        assert [v for v in violations if v.rule_id == "R004"] == []
        r009_violations = [v for v in violations if v.rule_id == "R009"]
        assert len(r009_violations) == 1
        assert r009_violations[0].severity == RuleSeverity.INFO

    def test_r004_exception_tag_still_works(self):
        """An exception tag on the def line still exempts a facade."""
        config = Config(service_paths=["**/*.py"])
        source = """
class Worker:
    @staticmethod
    def run(x: int):
        return x

def my_function(x: int):  # facade - celery schedule
    return Worker.run(x)
"""
        violations = _lint_source(source, config)
        assert [v for v in violations if v.rule_id == "R004"] == []

    def test_r004_nested_attribute_access_is_not_a_facade(self):
        """A lowercase attribute chain is not a class reference, so no facade is reported."""
        config = Config(service_paths=["**/*.py"])
        source = """
class Services:
    pass

_svc = Services()
_svc.user_service = type('UserService', (), {'get_user': lambda self, id: id})()

def get_user(user_id: int):
    return _svc.user_service.get_user(user_id)
"""
        violations = _lint_source(source, config)
        assert [v for v in violations if v.rule_id == "R004"] == []
