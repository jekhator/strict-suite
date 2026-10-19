"""Good example: module-level shapes that are exempt from R009."""

import functools


def __getattr__(name: str) -> str:
    """Module-level attribute hook."""
    return name


def __dir__() -> list[str]:
    """Module-level directory hook."""
    return []


def pytest_configure(config: object) -> None:
    """Pytest hook function."""
    return None


@functools.cache
def cached_lookup(key: str) -> str:
    """Decorated framework registration point."""
    return key


def scale_value(value: int) -> int:  # module-level: stateless conversion with no owning class
    """Convert a value."""
    return value * 2


def shift_value(value: int) -> int:
    """Module-level: stateless shift with no owning class."""
    return value + 1


class Holder:
    """Owning class for the default shape."""

    def run(self) -> None:
        """Run the holder."""
        return None
