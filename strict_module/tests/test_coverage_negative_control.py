"""Negative control test for coverage validation."""

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestNegativeControl:
    """Test coverage by exercising specific code paths."""

    def test_r001_with_return_type_dict_str_any(self, tmp_path):
        """Exercise R001 return type coverage with Dict[str, Any]."""
        code = '''"""Service file."""
from typing import Any, Dict

class ServiceClass:
    """Service with bad return type."""

    def process(self) -> Dict[str, Any]:
        """Process."""
        return {}
'''
        test_file = tmp_path / "service.py"
        test_file.write_text(code)

        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r001_violations = [v for v in violations if v.rule_id == "R001"]
        assert len(r001_violations) >= 1
        assert any("Dict[str, Any]" in v.message for v in r001_violations)

    def test_r006_with_return_type_any(self, tmp_path):
        """Exercise R006 return type coverage with typing.Any."""
        code = '''"""Service file."""
from typing import Any

class ServiceClass:
    """Service with bad return type."""

    def process(self) -> Any:
        """Process."""
        return None
'''
        test_file = tmp_path / "service.py"
        test_file.write_text(code)

        config = Config(
            service_paths=["**/*.py"],
            dto_paths=["**/dtos.py"],
            r006_paths=["**/*.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(test_file)
        r006_violations = [v for v in violations if v.rule_id == "R006"]
        assert len(r006_violations) >= 1
        assert any("return type" in v.message.lower() for v in r006_violations)
