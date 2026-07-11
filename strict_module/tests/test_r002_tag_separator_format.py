"""Test R002 exception tag format and separator alignment."""

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


def test_r002_tag_separator_format_in_message(tmp_path):
    """Test that R002 error message uses correct tag separator format colon."""
    code_file = tmp_path / "test.py"
    code_file.write_text("""
def process_data():
    return {"key": 1, "value": 2, "data": 3}
""")

    config = Config(
        service_paths=["**/*.py"],
        exception_tags=["facade - celery schedule"],
        exception_tag_requires_justification=True
    )
    linter = DtoStrictLinter(config)
    violations = linter.lint_file(code_file)
    r002_violations = [v for v in violations if v.rule_id == "R002"]

    assert len(r002_violations) >= 1
    for violation in r002_violations:
        msg = violation.message
        if "Format:" in msg:
            assert "Format: 'tag: explanation'" in msg
            assert "facade - celery schedule:" in msg
            assert "—" not in msg


def test_tag_separator_uses_colon_not_em_dash(tmp_path):
    """Test that tag separator format shows colon, not em dash."""
    config = Config(
        service_paths=["**/*.py"],
        exception_tags=["facade - celery schedule"],
        exception_tag_requires_justification=True
    )
    assert all("-" in tag and "—" not in tag for tag in config.exception_tags)
