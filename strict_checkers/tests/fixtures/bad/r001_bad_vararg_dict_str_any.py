"""Bad: Dict[str, Any] in *args annotation."""

from typing import Any, Dict


class ServiceClass:
    """Service with bad vararg."""

    def process(self, *args: Dict[str, Any]) -> None:
        """Process with Dict[str, Any] in vararg."""
        pass
