"""Bad: typing.Any in *args annotation."""

from typing import Any


class ServiceClass:
    """Service with bad vararg."""

    def process(self, *args: Any) -> None:
        """Process with Any in vararg."""
        pass
