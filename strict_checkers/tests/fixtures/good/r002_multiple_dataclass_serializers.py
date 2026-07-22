"""Good example: multiple dataclasses with to_* serializer methods are all exempt from R002."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FirstDTO:
    """First data transfer object."""

    id: int
    name: str
    status: str

    def to_dict(self) -> dict:
        """Serialize to dict (exempt from R002)."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class SecondDTO:
    """Second data transfer object (tests state reset across classes)."""

    user_id: int
    email: str
    created_at: str
    updated_at: str

    def to_log_extra(self) -> dict:
        """Return log metadata dict (exempt from R002)."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class RegularClass:
    """Plain class (not a dataclass) with to_* method."""

    def __init__(self, value: str):
        self.value = value

    def to_dict(self) -> dict:
        """This should STILL be flagged because class is not @dataclass."""
        return {
            "value": self.value,
            "extra1": "data1",
            "extra2": "data2",
        }
