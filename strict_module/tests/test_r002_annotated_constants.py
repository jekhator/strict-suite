"""Tests for R002 rule on annotated constants.

Verifies that R002 correctly skips annotated module-level and class-level
constants while still flagging actual inline dict literals in function bodies.
"""

import ast
import textwrap
from pathlib import Path

from strict_module.checkers import R002Checker
from strict_module.config import Config


class TestR002AnnotatedConstants:
    """Test suite for related functionality."""

    def test_r002_skips_annotated_module_constant(self):
        """R002 should skip annotated module-level constants (typed declarations)."""
        code = textwrap.dedent("""
            DISPLAY_LABELS: dict[str, str] = {
                "draft": "Draft",
                "active": "Active",
                "archived": "Archived",
            }
        """).strip()

        config = Config(service_paths=["apps/*/services/*.py"])
        tree = ast.parse(code)
        checker = R002Checker(Path("apps/foo/services/m.py"), code, config)
        checker.visit(tree)

        # Should report 0 R002 violations
        assert len(checker.violations) == 0, (
            f"Expected 0 violations, got {len(checker.violations)}"
        )

    def test_r002_flags_unannotated_module_constant(self):
        """R002 should flag unannotated module-level dicts (ambiguous intent)."""
        code = textwrap.dedent("""
            DISPLAY_LABELS = {
                "draft": "Draft",
                "active": "Active",
                "archived": "Archived",
            }
        """).strip()

        config = Config(service_paths=["apps/*/services/*.py"])
        tree = ast.parse(code)
        checker = R002Checker(Path("apps/foo/services/m.py"), code, config)
        checker.visit(tree)

        # Should report 1 R002 violation
        assert len(checker.violations) == 1, (
            f"Expected 1 violation, got {len(checker.violations)}"
        )
        assert checker.violations[0].rule_id == "R002"

    def test_r002_flags_inline_dict_in_function(self):
        """R002 should still flag inline dict literals inside function bodies."""
        code = textwrap.dedent("""
            def process():
                return {"a": "A", "b": "B", "c": "C"}
        """).strip()

        config = Config(service_paths=["apps/*/services/*.py"])
        tree = ast.parse(code)
        checker = R002Checker(Path("apps/foo/services/m.py"), code, config)
        checker.visit(tree)

        # Should report 1 R002 violation
        assert len(checker.violations) == 1, (
            f"Expected 1 violation, got {len(checker.violations)}"
        )
        assert checker.violations[0].rule_id == "R002"

    def test_r002_skips_annotated_class_constant(self):
        """R002 should skip annotated class-level constants."""
        code = textwrap.dedent("""
            class Config:
                DISPLAY: dict[str, str] = {"a": "A", "b": "B", "c": "C"}
        """).strip()

        config = Config(service_paths=["apps/*/services/*.py"])
        tree = ast.parse(code)
        checker = R002Checker(Path("apps/foo/services/m.py"), code, config)
        checker.visit(tree)

        # Should report 0 R002 violations
        assert len(checker.violations) == 0, (
            f"Expected 0 violations, got {len(checker.violations)}"
        )

    def test_r002_mixed_constants_and_inline(self):
        """Mixed: annotated constant should pass, inline in function should fail."""
        code = textwrap.dedent("""
            DISPLAY_LABELS: dict[str, str] = {
                "draft": "Draft",
                "active": "Active",
                "archived": "Archived",
            }

            def get_status():
                return {"pending": "Pending", "approved": "Approved", "rejected": "Rejected"}
        """).strip()

        config = Config(service_paths=["apps/*/services/*.py"])
        tree = ast.parse(code)
        checker = R002Checker(Path("apps/foo/services/m.py"), code, config)
        checker.visit(tree)

        # Should report 1 R002 violation (only the inline dict in the function)
        assert len(checker.violations) == 1, (
            f"Expected 1 violation, got {len(checker.violations)}"
        )
        assert checker.violations[0].rule_id == "R002"
        # Line 8 is the return statement line (1-indexed)
        assert checker.violations[0].line == 8

    def test_r002_respects_exception_tags(self):
        """R002 should still respect exception tags on inline dicts."""
        code = textwrap.dedent("""
            def process():
                return {"a": "A", "b": "B", "c": "C"}  # facade: transient event
        """).strip()

        config = Config(
            service_paths=["apps/*/services/*.py"], exception_tags=["facade"]
        )
        tree = ast.parse(code)
        checker = R002Checker(Path("apps/foo/services/m.py"), code, config)
        checker.visit(tree)

        # Should report 0 R002 violations (exception tag present)
        assert len(checker.violations) == 0, (
            f"Expected 0 violations, got {len(checker.violations)}"
        )

    def test_r002_non_service_file(self):
        """R002 should not flag dicts in non-service files."""
        code = textwrap.dedent("""
            DISPLAY_LABELS = {
                "draft": "Draft",
                "active": "Active",
                "archived": "Archived",
            }
        """).strip()

        config = Config(service_paths=["apps/*/services/*.py"])
        # Non-service file
        tree = ast.parse(code)
        checker = R002Checker(Path("apps/foo/models.py"), code, config)
        checker.visit(tree)

        # Should report 0 R002 violations (not a service file)
        assert len(checker.violations) == 0, (
            f"Expected 0 violations, got {len(checker.violations)}"
        )
