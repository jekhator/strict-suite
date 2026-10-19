"""Pytest fixtures for strict-module tests."""

from pathlib import Path

import pytest


@pytest.fixture
def fixture_dir():
    """Path to the linter fixture tree (good and bad examples).

    Used by: TestCli, TestR001DictStrAny, TestR001VarArgKwarg, TestR002InlineDict,
    TestR002MultipleDataclassRegression, TestR002SerializerExemption,
    TestR002TagJustification, TestR003DataclassTrio, TestR004ModuleFacade,
    TestR005ValidatorPattern, TestR006VarArgKwarg, TestR007FixtureDecorators,
    TestR007Fixtures, TestR008TestFunctions, TestR009ModuleLevelFunctions,
    TestR010LegacyTypingABC, TestR011RaiseLiterals.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def config():
    """A default Config instance.

    Used by: TestBranchCoverage, TestConfigLoading, TestCoverageTargets,
    TestDirectASTManipulation, TestErrorHandlingPaths, TestExceptionHandling,
    TestFinalCoverageBoost, TestInfoSeverityLevel, TestLinterEdgeCases,
    TestLinterFileHandling, TestR012EdgeCases, TestR012FitsOneLineStays,
    TestR012RecoveryPaths, TestR013CoveragePaths, TestR013EdgeCases, TestR013MoreEdgeCases,
    TestR013SignatureGrouping, TestR014CoveragePaths, TestR014EdgeCases,
    TestR014KwargCallGrouping, TestR014MoreEdgeCases, TestR015CoveragePaths,
    TestR015EdgeCases, TestR015WrapPathSeparation, TestSeverityOverridesFix,
    test_optimization_pass._lint, test_r004_auto_detect._lint_source.
    """
    from strict_config._config import Config

    return Config()


@pytest.fixture
def project_dir(tmp_path):
    """A temporary project with a bad and a good service file and a pyproject for CLI tests.

    Used by: TestCLILocCap, TestCLIRealInvocations.
    """
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

class OrderService:
    \"\"\"Service for processing orders.\"\"\"

    def process_order(self, data: OrderRequest) -> dict:
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
def temp_project_with_test_files(tmp_path):
    """A temporary project with source files and test files that loc-cap must exempt.

    Used by: TestLocCapTestExemption.
    """
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


@pytest.fixture
def run_cli(monkeypatch, capsys):
    """Run the strict-module CLI in-process and return (exit_code, stdout, stderr).

    Used by: TestUnreadableInputs.
    """

    def _run(argv):
        monkeypatch.setattr("sys.argv", ["strict-module", *argv])
        from strict_module.cli import main

        code = main()
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run
