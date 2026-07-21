"""Tests for R001: Dict[str, Any] in service signatures."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR001DictStrAny:
    """Test suite for related functionality."""

    def test_r001_good_no_dict_str_any(self, fixture_dir):
        """Good: no Dict[str, Any] in signatures."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "good" / "r001_good_basic.py")
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) == 0

    def test_r001_bad_param_dict_str_any(self, fixture_dir):
        """Bad: Dict[str, Any] in parameter."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r001_bad_param.py")
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) >= 1
        assert any("Dict[str, Any]" in v.message for v in r001_violations)

    def test_r001_bad_return_dict_str_any(self, fixture_dir):
        """Bad: Dict[str, Any] in return type."""
        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(fixture_dir / "bad" / "r001_bad_return.py")
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) >= 1
