"""Bad: typing.Any in **kwargs annotation."""

from typing import Any


class ServiceClass:
    """Service with bad kwarg."""

    def process(self, **kwargs: Any) -> None:
        """Process with Any in kwarg."""
        pass
