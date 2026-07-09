"""Good example: dataclass with frozen=True, slots=True, repr=False."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, repr=False)
class GoodUserDTO:
    """User DTO with all required parameters."""

    user_id: int
    email: str
    name: str


@dataclass(frozen=True, slots=True, repr=False)
class GoodConfigDTO:
    """Config DTO with all required parameters."""

    timeout: int
    host: str
