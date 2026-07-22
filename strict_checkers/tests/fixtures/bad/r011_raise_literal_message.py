"""Bad: String literals in raise statements."""


def process_query(query):
    """Process query with inline error message."""
    if not query:
        raise ValueError("Query cannot be empty")


def calculate_value(data):
    """Calculate with f-string error."""
    if data is None:
        invalid_data = True
        raise RuntimeError(f"Invalid data: {invalid_data}")


class DataProcessor:
    """Class with literal errors."""

    def validate(self, item):
        """Validate item with keyword argument literal."""
        if item is None:
            raise TypeError(message="Item must not be None")

    def transform(self, value):
        """Transform with f-string."""
        if not isinstance(value, str):
            raise ValueError(f"Expected str, got {type(value).__name__}")
