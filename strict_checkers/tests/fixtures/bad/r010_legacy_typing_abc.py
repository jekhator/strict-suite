"""Bad: Using legacy typing aliases for ABCs."""

from typing import Callable, Mapping, Iterable, Awaitable


class DataProcessor:
    """Processor using legacy typing ABCs."""

    def handle_callable(self, func: Callable) -> None:
        """Accept a callable using legacy typing."""
        func()

    def process_mapping(self, data: Mapping) -> None:
        """Process a mapping using legacy typing."""
        return data  # type: ignore[return-value]

    def process_iterable(self, items: Iterable) -> None:
        """Process an iterable using legacy typing."""
        return items  # type: ignore[return-value]

    async def handle_awaitable(self) -> Awaitable:
        """Return an awaitable using legacy typing."""
        return None  # type: ignore[return-value]
