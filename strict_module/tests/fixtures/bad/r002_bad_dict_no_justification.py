"""Bad: inline dict with exception tag but no justification."""

from typing import Any


class ServiceClass:
    """Service with bad inline dict."""

    def process(self) -> dict:
        """Process with dict that has tag but no justification."""
        data = {  # noqa: facade - missing colon here
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        return data
