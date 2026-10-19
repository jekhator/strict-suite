"""Bad example: a docstring that mentions the tag word as prose does not exempt a function."""


def strip_prefix(value: str) -> str:
    """Module-level helper that strips the prefix from a value."""
    return value.removeprefix("prefix-")
