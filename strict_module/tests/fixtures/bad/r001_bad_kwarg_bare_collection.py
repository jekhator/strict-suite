"""Bad: bare collection type in **kwargs annotation."""

from typing import Dict


class ServiceClass:
    """Service with bad kwarg."""

    def process(self, **kwargs: list) -> None:
        """Process with bare list in kwarg."""
        pass
