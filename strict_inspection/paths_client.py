"""Path classification utilities."""

import fnmatch
from pathlib import Path

TEST_BASENAME = "conftest.py"
TEST_PREFIX = "test_"


class PathClassifier:
    """Classify file paths for linting scope."""

    @staticmethod
    def is_test_file(file_path: Path) -> bool:
        """Check if file is a test file by basename (conftest.py or test_*.py) for linting."""
        basename = file_path.name
        return basename == TEST_BASENAME or basename.startswith(TEST_PREFIX)

    @staticmethod
    def is_loc_test_file(file_path: Path) -> bool:
        """Check if file is a test file (conftest.py, test_*.py, or under tests/ directory)."""
        if PathClassifier.is_test_file(file_path):
            return True
        return "/tests/" in str(file_path) or str(file_path).startswith("tests/")

    @staticmethod
    def is_service_path(file_path: Path, service_paths: list[str]) -> bool:
        """Check if file path matches a service path pattern (excluding test files)."""
        return PathClassifier._matches_any(file_path, service_paths)

    @staticmethod
    def is_dto_path(file_path: Path, dto_paths: list[str]) -> bool:
        """Check if file path matches a DTO path pattern (excluding test files)."""
        return PathClassifier._matches_any(file_path, dto_paths)

    @staticmethod
    def _matches_any(file_path: Path, patterns: list[str]) -> bool:
        """Check that a non-test file matches at least one glob pattern."""
        if PathClassifier.is_test_file(file_path):
            return False
        return any(fnmatch.fnmatch(str(file_path), pattern) for pattern in patterns)
