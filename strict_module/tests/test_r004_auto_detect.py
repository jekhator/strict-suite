"""Tests for R004 auto-detect class-method-wrapping pattern (Issue #1)."""

import pytest
from pathlib import Path
from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


@pytest.fixture
def fixture_dir():
    """Get fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def config():
    """Create a test config."""
    return Config(
        service_paths=["**/*.py"],
        dto_paths=["**/dtos.py"],
        exception_tags=["facade - celery schedule", "FRAMEWORK"],
    )


def test_r004_auto_detect_class_method_wrapper(config):
    """R004: Auto-detect class-method delegation pattern (no tag needed)."""
    source = """
class UserService:
    @staticmethod
    def get_user(user_id: int):
        return user_id

_service = UserService()

def get_user_wrapper(user_id: int):
    # This is a wrapper that delegates to class method - no tag needed
    return _service.get_user(user_id)

def another_wrapper(user_id: int):
    # Another wrapper pattern - should skip (no violation)
    return UserService.get_user(user_id)
"""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source)
        f.flush()
        path = Path(f.name)

    try:
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(path)
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert len(r004_violations) == 0, (
            "Class-method wrappers should be auto-detected as legitimate"
        )
    finally:
        path.unlink()


def test_r004_pure_utility_function_needs_tag(config):
    """R004: Pure utility function (no class-method calls) should have tag."""
    source = """
def pure_utility(x: int):
    # This is a pure utility with business logic - needs tag
    return x * 2
"""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source)
        f.flush()
        path = Path(f.name)

    try:
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(path)
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert len(r004_violations) >= 1, "Pure utility without tag should be flagged"
    finally:
        path.unlink()


def test_r004_exception_tag_still_works(config):
    """R004: Exception tag still works as override."""
    source = """
def my_function(x: int):  # facade - celery schedule
    return x * 2
"""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source)
        f.flush()
        path = Path(f.name)

    try:
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(path)
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert len(r004_violations) == 0, "Exception tag should allow function"
    finally:
        path.unlink()


def test_r004_nested_attribute_access(config):
    """R004: Auto-detect nested attribute access (obj.service.method())."""
    source = """
class Services:
    pass

_svc = Services()
_svc.user_service = type('UserService', (), {'get_user': lambda self, id: id})()

def get_user(user_id: int):
    # Wrapper with nested attribute access - auto-detected
    return _svc.user_service.get_user(user_id)
"""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source)
        f.flush()
        path = Path(f.name)

    try:
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(path)
        r004_violations = [v for v in violations if v.rule_id == "R004"]
        assert len(r004_violations) == 0, (
            "Nested attribute method calls should be auto-detected"
        )
    finally:
        path.unlink()
