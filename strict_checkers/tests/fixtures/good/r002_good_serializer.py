"""Good example: dict literals in to_* methods of dataclasses are exempt from R002."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserDTO:
    """User data transfer object."""

    user_id: int
    name: str
    email: str

    def to_dict(self) -> dict:
        """Serialize to dict (exempt from R002)."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
        }


@dataclass(frozen=True, slots=True)
class ConfigDTO:
    """Config DTO."""

    timeout: int
    retries: int
    host: str

    def to_json_dict(self) -> dict:
        """Convert to JSON-serializable dict (exempt from R002)."""
        return {
            "timeout": self.timeout,
            "retries": self.retries,
            "host": self.host,
        }
