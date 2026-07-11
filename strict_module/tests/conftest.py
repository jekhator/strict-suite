"""Pytest fixtures for strict-module tests."""

import pytest
from pathlib import Path


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
def test_project_dir(tmp_path):
    """Create a temporary project for CLI testing."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    src_dir = project_root / "src"
    src_dir.mkdir()
    (src_dir / "__init__.py").touch()

    return project_root
