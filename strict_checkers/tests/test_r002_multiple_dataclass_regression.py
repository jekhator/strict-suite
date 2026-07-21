"""Regression test: multiple dataclasses with to_* serializer methods (state reset per class)."""

from strict_config._config import Config
from strict_linter import DtoStrictLinter


class TestR002MultipleDataclassRegression:
    """Test suite for related functionality."""

    def test_r002_multiple_dataclass_serializers_both_exempt(self, fixture_dir):
        """Both FirstDTO and SecondDTO to_* methods should be exempt.

        This tests that state is properly reset per class - the second dataclass
        should not be affected by processing the first.
        """
        config = Config(
            service_paths=["*/**/*.py", "tests/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "good" / "r002_multiple_dataclass_serializers.py"
        )
        r002_violations = [v for v in violations if v.rule_id == "R002"]

        # FirstDTO.to_dict() and SecondDTO.to_log_extra() should be exempt
        # Only RegularClass.to_dict() should be flagged (at line 50)
        dataclass_violations = [v for v in r002_violations if v.line != 50]
        assert len(dataclass_violations) == 0, (
            "Dataclass to_* methods should be exempt. "
            f"Got {len(dataclass_violations)} violations in dataclass methods"
        )

    def test_r002_plain_class_to_method_still_flagged(self, fixture_dir):
        """Plain class (non-dataclass) to_* methods should still be flagged.

        Tests that the exemption only applies to @dataclass-decorated classes,
        not all classes with to_* methods.
        """
        config = Config(
            service_paths=["*/**/*.py", "tests/fixtures/**/*.py"],
            dto_paths=["**/dtos.py"],
        )
        linter = DtoStrictLinter(config)
        violations = linter.lint_file(
            fixture_dir / "good" / "r002_multiple_dataclass_serializers.py"
        )
        r002_violations = [v for v in violations if v.rule_id == "R002"]

        # RegularClass.to_dict() should be flagged (not a dataclass)
        assert len(r002_violations) >= 1, (
            "Plain class to_dict() method with 3+ keys should be flagged"
        )

        # Verify the violation is for the plain class dict (line 50)
        assert any(v.line == 50 for v in r002_violations), (
            "Violation should be at line 50 (RegularClass.to_dict return)"
        )
