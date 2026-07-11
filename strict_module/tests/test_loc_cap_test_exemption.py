"""Tests for loc-cap test file exemption."""

import pytest
import tempfile
from pathlib import Path
from strict_module.loc_cap import find_python_files


@pytest.fixture
def temp_project():
    """Create a temporary project structure with test and source files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

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

        yield root


def test_loc_cap_exempts_test_basename(temp_project):
    """Test files matching test_*.py are exempt."""
    files = find_python_files(str(temp_project))
    # test_module.py (600 lines) should not appear
    for path, loc in files.items():
        assert "test_module.py" not in path, "test_*.py files should be exempt"


def test_loc_cap_exempts_conftest(temp_project):
    """conftest.py files are exempt."""
    files = find_python_files(str(temp_project))
    # conftest.py (700 lines) should not appear
    for path in files.keys():
        assert "conftest.py" not in path, "conftest.py should be exempt"


def test_loc_cap_exempts_tests_directory(temp_project):
    """Files under tests/ directory are exempt."""
    files = find_python_files(str(temp_project))
    # test_helper.py under tests/ (800 lines) should not appear
    for path in files.keys():
        assert "/tests/" not in path and not path.startswith("tests/"), (
            "Files under tests/ should be exempt"
        )


def test_loc_cap_counts_source_files(temp_project):
    """Source files that are not test files are counted."""
    files = find_python_files(str(temp_project))
    # src/module.py (500 lines) should be counted
    found_src = False
    for path, loc in files.items():
        if "src/module.py" in path or "src" + chr(92) + "module.py" in path:
            found_src = True
            assert loc == 500, "Source file should be counted with correct line count"
    assert found_src, "Source file should be present in results"
