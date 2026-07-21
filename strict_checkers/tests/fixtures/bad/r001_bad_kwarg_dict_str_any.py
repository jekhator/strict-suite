"""Bad: Dict[str, Any] in **kwargs annotation."""

from typing import Any, Dict


class ServiceClass:
    """Service with bad kwarg."""

    def process(self, **kwargs: Dict[str, Any]) -> None:
        """Process with Dict[str, Any] in kwarg."""
        pass
