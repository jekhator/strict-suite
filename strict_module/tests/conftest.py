"""Pytest fixtures for strict-module tests."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def fixture_dir():
    """Get fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def config():
    """Get default config."""
    from strict_module.config import Config

    return Config()


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with Python files."""
    project_root = tmp_path / "project"
    project_root.mkdir()

    src_dir = project_root / "src"
    src_dir.mkdir()
    (src_dir / "__init__.py").touch()

    return project_root


@pytest.fixture
def project_dir(tmp_path):
    """Create a temporary project with test files for CLI testing."""
    project_root = tmp_path / "cli_project"

    bad_service_file = project_root / "apps" / "services" / "bad.py"
    bad_service_file.parent.mkdir(parents=True, exist_ok=True)
    bad_service_file.write_text(
        """
\"\"\"Bad service with Dict[str, Any].\"\"\"
from typing import Any, Dict

def process_order(data: Dict[str, Any]) -> dict:
    \"\"\"Process order data.\"\"\"
    return {"status": "ok"}
"""
    )

    good_service_file = project_root / "apps" / "services" / "good.py"
    good_service_file.write_text(
        """
\"\"\"Good service without Dict[str, Any].\"\"\"
from dataclasses import dataclass

@dataclass
class OrderRequest:
    customer_id: int
    amount: float

def process_order(data: OrderRequest) -> dict:
    \"\"\"Process order data.\"\"\"
    return {"status": "ok"}
"""
    )

    pyproject = project_root / "pyproject.toml"
    pyproject.write_text(
        """
[tool.strict-module]
service_paths = ["apps/*/services/*.py"]
"""
    )

    return project_root


@pytest.fixture
def cli_project_dir(project_dir):
    """CLI project directory fixture."""
    return project_dir


@pytest.fixture
def temp_project_with_test_files(tmp_path):
    """Create a temporary project structure with test and source files."""
    root = tmp_path

    # Create source file (should be counted)
    src_file = root / "src" / "module.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("x = 1\n" * 500)  # 500 lines

    # Create test_*.py file (should be exempt)
    test_file = root / "test_module.py"
    test_file.write_text("x = 1\n" * 600)  # 600 lines (would normally warn)

    # Create conftest.py (should be exempt)
    conftest = root / "conftest.py"
    conftest.write_text("x = 1\n" * 700)  # 700 lines (would normally error)

    # Create file under tests/ directory (should be exempt)
    tests_dir = root / "tests"
    tests_dir.mkdir()
    test_in_dir = tests_dir / "test_helper.py"
    test_in_dir.write_text("x = 1\n" * 800)  # 800 lines (would normally error)

    # Create another source file under src/tests/ (should be exempt because under tests/)
    src_test_file = root / "src" / "tests" / "helper.py"
    src_test_file.parent.mkdir(parents=True, exist_ok=True)
    src_test_file.write_text("x = 1\n" * 750)  # 750 lines

    return root
