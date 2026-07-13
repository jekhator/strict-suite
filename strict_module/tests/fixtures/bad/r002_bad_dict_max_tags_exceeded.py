"""Bad: multiple exception tags exceeding max per file."""

from typing import Any


class ServiceClass:
    """Service with multiple bad inline dicts."""

    def process(self) -> dict:
        """First dict."""
        data1 = {  # noqa: facade - first
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }

        data2 = {  # noqa: facade - second
            "a": 1,
            "b": 2,
            "c": 3,
        }

        data3 = {  # noqa: facade - third
            "x": "ex",
            "y": "why",
            "z": "zee",
        }

        return data1
