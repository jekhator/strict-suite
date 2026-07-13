"""Bad: bare collection type in *args annotation."""

from typing import Dict


class ServiceClass:
    """Service with bad vararg."""

    def process(self, *args: dict) -> None:
        """Process with bare dict in vararg."""
        pass
