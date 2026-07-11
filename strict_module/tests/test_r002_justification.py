"""Tests for R002: exception_tag_requires_justification mode."""

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


def test_r002_tag_without_justification(tmp_path):
    """Tag without justification flagged when required."""
    bad_file = tmp_path / "bad_tag.py"
    bad_file.write_text(
        """
def process():  # facade - celery schedule
    x = {"a": 1, "b": 2, "c": 3}
    return x
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        exception_tags=["facade - celery schedule"],
        exception_tag_requires_justification=True,
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(bad_file)
    r002_violations = [v for v in violations if v.rule_id == "R002"]
    assert len(r002_violations) >= 1
    assert any("justification" in v.message.lower() for v in r002_violations)


def test_r002_tag_with_justification(tmp_path):
    """Tag with justification allowed when required."""
    good_file = tmp_path / "good_tag.py"
    good_file.write_text(
        """
def process():  # facade - celery schedule: transient event payload
    x = {"a": 1, "b": 2, "c": 3}
    return x
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        exception_tags=["facade - celery schedule"],
        exception_tag_requires_justification=True,
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(good_file)
    r002_violations = [v for v in violations if v.rule_id == "R002"]
    assert len(r002_violations) == 0


def test_r002_max_exception_tags(tmp_path):
    """Exceeding max_exception_tags_per_file triggers violation."""
    bad_file = tmp_path / "too_many_tags.py"
    bad_file.write_text(
        """
def process1():  # facade - celery schedule
    x = {"a": 1, "b": 2, "c": 3}
    return x

def process2():  # facade - celery schedule
    y = {"d": 4, "e": 5, "f": 6}
    return y

def process3():  # facade - celery schedule
    z = {"g": 7, "h": 8, "i": 9}
    return z
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        exception_tags=["facade - celery schedule"],
        max_exception_tags_per_file=2,
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(bad_file)
    r002_violations = [v for v in violations if v.rule_id == "R002"]
    # Should flag the third tag usage
    assert len(r002_violations) >= 1


def test_r002_no_justification_required(tmp_path):
    """Tag without justification allowed when not required."""
    good_file = tmp_path / "tag_no_justification.py"
    good_file.write_text(
        """
def process():  # facade - celery schedule
    x = {"a": 1, "b": 2, "c": 3}
    return x
"""
    )
    config = Config(
        service_paths=["**/*.py"],
        exception_tags=["facade - celery schedule"],
        exception_tag_requires_justification=False,  # default
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(good_file)
    r002_violations = [v for v in violations if v.rule_id == "R002"]
    assert len(r002_violations) == 0
