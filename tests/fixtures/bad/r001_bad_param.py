"""Bad example: Dict[str, Any] in service function parameters."""

from typing import Any, Dict


def process_user_config(config: Dict[str, Any]) -> None:
    """Bad: Dict[str, Any] in parameter."""
    pass


def validate_settings(settings: dict[str, Any]) -> bool:
    """Bad: dict[str, Any] in parameter."""
    return True
