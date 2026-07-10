"""Bad example: dict literals in non-to_* methods or plain classes still violate R002."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserDTO:
    """User DTO where non-serializer methods should still be flagged."""

    user_id: int
    name: str
    email: str

    def get_metadata(self) -> dict:
        """Not a to_* method, so the inline dict should be flagged."""
        return {
            "created_at": "2025-01-01",
            "updated_at": "2025-01-02",
            "status": "active",
        }


class PlainClass:
    """Plain class (not a dataclass) with to_* method should still flag."""

    def to_dict(self) -> dict:
        """Not a dataclass method, so even to_* is flagged."""
        return {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
        }
