"""Bad example: Dict[str, Any] in service function return type."""

from typing import Any, Dict


def get_user_config() -> Dict[str, Any]:
    """Bad: Dict[str, Any] in return type."""
    return {"user_id": 123}


def fetch_settings() -> dict[str, Any]:
    """Bad: dict[str, Any] in return type."""
    return {"timeout": 30}
