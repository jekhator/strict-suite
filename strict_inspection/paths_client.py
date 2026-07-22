"""Path classification utilities."""

import fnmatch
from pathlib import Path


class PathClassifier:
    """Classify file paths for linting scope."""

    @staticmethod
    def is_test_file(file_path: Path) -> bool:
        """Check if file is a test file by basename (conftest.py or test_*.py) for linting."""
        basename = file_path.name
        if basename == "conftest.py" or basename.startswith("test_"):
            return True
        return False

    @staticmethod
    def is_loc_test_file(file_path: Path) -> bool:
        """Check if file is a test file (conftest.py, test_*.py, or under tests/ directory)."""
        basename = file_path.name
        if basename == "conftest.py" or basename.startswith("test_"):
            return True
        if "/tests/" in str(file_path) or str(file_path).startswith("tests/"):
            return True
        return False

    @staticmethod
    def is_service_path(file_path: Path, service_paths: list[str]) -> bool:
        """Check if file path matches a service path pattern (excluding test files)."""
        if PathClassifier.is_test_file(file_path):
            return False
        for pattern in service_paths:
            if fnmatch.fnmatch(str(file_path), pattern):
                return True
        return False

    @staticmethod
    def is_dto_path(file_path: Path, dto_paths: list[str]) -> bool:
        """Check if file path matches a DTO path pattern (excluding test files)."""
        if PathClassifier.is_test_file(file_path):
            return False
        for pattern in dto_paths:
            if fnmatch.fnmatch(str(file_path), pattern):
                return True
        return False
