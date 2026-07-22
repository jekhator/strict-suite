"""Good: Using modern collections.abc for ABCs."""

from collections.abc import Awaitable, Callable, Iterable, Mapping
from typing import Any, ParamSpec, TypeVar


class DataProcessor:
    """Processor using modern collections.abc ABCs."""

    def handle_callable(self, func: Callable) -> None:
        """Accept a callable using collections.abc."""
        func()

    def process_mapping(self, data: Mapping) -> None:
        """Process a mapping using collections.abc."""
        return data  # type: ignore[return-value]

    def process_iterable(self, items: Iterable) -> None:
        """Process an iterable using collections.abc."""
        return items  # type: ignore[return-value]

    async def handle_awaitable(self) -> Awaitable:
        """Return an awaitable using collections.abc."""
        return None  # type: ignore[return-value]


T = TypeVar("T")
P = ParamSpec("P")


def generic_function(value: Any) -> T:  # type: ignore[type-var]
    """Typing.Any and TypeVar are still from typing (not collections.abc)."""
    return value
