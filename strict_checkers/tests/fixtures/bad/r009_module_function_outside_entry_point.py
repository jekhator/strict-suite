"""Bad: Module-level function outside allowed entry points."""


def process_data(data):
    """This function should be in a class."""
    return data.upper()


def calculate_sum(a, b):
    """Another module-level function that should be in a class."""
    return a + b
