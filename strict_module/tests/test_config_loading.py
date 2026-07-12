"""Tests for configuration loading."""

from pathlib import Path

from strict_module.config import Config


def test_config_defaults():
    """Test default configuration."""
    config = Config()
    assert "apps/*/services/*.py" in config.service_paths
    assert "**/dtos.py" in config.dto_paths
    assert "facade - celery schedule" in config.exception_tags
    assert len(config.disabled_rules) == 0


def test_config_is_rule_enabled():
    """Test rule enable/disable logic."""
    config = Config(disabled_rules=["R001", "R002"])
    assert not config.is_rule_enabled("R001")
    assert not config.is_rule_enabled("R002")
    assert config.is_rule_enabled("R003")


def test_config_from_nonexistent_pyproject():
    """Test loading from nonexistent config file."""
    config = Config.from_pyproject(Path("/nonexistent/pyproject.toml"))
    # Should return defaults
    assert config.service_paths == ["apps/*/services/*.py", "**/services/*.py"]


def test_config_from_pyproject(tmp_path):
    """Test loading from real pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.dto-strict]
service_paths = ["custom/services/*.py"]
disabled_rules = ["R005"]
exception_tags = ["CUSTOM_TAG"]
"""
    )

    config = Config.from_pyproject(pyproject)
    assert config.service_paths == ["custom/services/*.py"]
    assert "R005" in config.disabled_rules
    assert "CUSTOM_TAG" in config.exception_tags
