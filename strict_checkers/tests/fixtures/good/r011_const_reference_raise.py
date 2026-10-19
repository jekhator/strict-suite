"""Good: Constants referenced in raise statements."""

import constants as const  # type: ignore[import-not-found]


def process_query(query):  # module-level: fixture helper with no owning class
    """Process query with const reference."""
    if not query:
        raise ValueError(const.ERR_QUERY_EMPTY)


def calculate_value(data):  # module-level: fixture helper with no owning class
    """Calculate with const attribute reference."""
    if data is None:
        raise RuntimeError(const.ERR_DATA_INVALID)


class DataProcessor:
    """Class with proper error references."""

    def validate(self, item):
        """Validate item using const."""
        if item is None:
            raise TypeError(const.ERR_ITEM_REQUIRED)

    def transform(self, value):
        """Transform using const reference."""
        if not isinstance(value, str):
            raise ValueError(const.ERR_TYPE_MISMATCH)


def bare_reraise():  # module-level: fixture helper with no owning class
    """Function with bare re-raise."""
    try:
        1 / 0
    except ValueError:
        raise


def no_args_error():  # module-level: fixture helper with no owning class
    """Function with no-arg raise."""
    if True:
        raise ValueError()


def from_clause(exc):  # module-level: fixture helper with no owning class
    """Function with from clause but const in original."""
    try:
        1 / 0
    except Exception as error:
        raise ValueError(const.ERR_X) from error
