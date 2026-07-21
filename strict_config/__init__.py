"""Configuration module for strict-module."""

from strict_config._config import Config, LocCapConfig
from strict_config._version import __version__
from strict_config.constants import *  # noqa: F401, F403

__all__ = ["Config", "LocCapConfig", "__version__"]
