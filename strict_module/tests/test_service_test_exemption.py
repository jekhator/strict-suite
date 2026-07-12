"""Tests for service test file exemption from R001, R004, R006 rules."""

import tempfile
from pathlib import Path

from strict_module.config import Config
from strict_module.linter import DtoStrictLinter


class TestServiceTestExemption:
    """Test suite for related functionality."""

    def test_service_test_file_exempt_from_r001_r004_r006(self):
        """Test files in services/ are exempt from R001, R004, R006.

        This test verifies that a conftest.py with:
        - module-level @pytest.fixture (would trigger R004 in production code)
        - @pytest.fixture with type[Any] (would trigger R006 in production code)
        are NOT flagged because the file is a test file.
        """
        config = Config(
            service_paths=["**/services/*.py"],
            r006_paths=["**/services/*.py"],
        )
        linter = DtoStrictLinter(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create services/tests/test_x/conftest.py
            services_dir = Path(tmpdir) / "services" / "tests" / "test_x"
            services_dir.mkdir(parents=True, exist_ok=True)

            conftest_path = services_dir / "conftest.py"
            conftest_path.write_text("""
import pytest
from typing import Any

@pytest.fixture
def f() -> type[Any]:
    '''A fixture with type[Any] - would trigger R006 in production.'''
    return dict

def helper_function():
    '''Module-level function without exception tag - would trigger R004 in production.'''
    return 42
""")

            violations = linter.lint_file(conftest_path)

            # Filter by rule IDs
            r001_violations = [v for v in violations if v.rule_id == "R001"]
            r004_violations = [v for v in violations if v.rule_id == "R004"]
            r006_violations = [v for v in violations if v.rule_id == "R006"]

            # None of these should trigger because the file is a test file
            assert len(r001_violations) == 0, (
                f"R001 should not trigger in test files: {r001_violations}"
            )
            assert len(r004_violations) == 0, (
                f"R004 should not trigger in test files: {r004_violations}"
            )
            assert len(r006_violations) == 0, (
                f"R006 should not trigger in test files: {r006_violations}"
            )

    def test_production_service_file_still_flagged_for_r001_r004_r006(self):
        """Verify that production code in services/ is still properly flagged.

        This ensures the exemption only applies to test files, not all service files.
        """
        config = Config(
            service_paths=["**/services/*.py"],
            r006_paths=["**/services/*.py"],
        )
        linter = DtoStrictLinter(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create services/handler.py (NOT a test file)
            services_dir = Path(tmpdir) / "services"
            services_dir.mkdir(parents=True, exist_ok=True)

            handler_path = services_dir / "handler.py"
            handler_path.write_text("""
from typing import Any

def process_data(data: dict[str, Any]) -> dict[str, Any]:
    '''Production code with Dict[str, Any] - should trigger R001 and R006.'''
    return data
""")

            violations = linter.lint_file(handler_path)

            # Filter by rule IDs
            r001_violations = [v for v in violations if v.rule_id == "R001"]
            r006_violations = [v for v in violations if v.rule_id == "R006"]

            # These should trigger because it's production code
            assert len(r001_violations) >= 1, (
                "R001 should trigger for production service code with Dict[str, Any]"
            )
            assert len(r006_violations) >= 1, (
                "R006 should trigger for production service code with Any"
            )
