"""Bad example: dataclass missing frozen, slots, or repr=False."""

from dataclasses import dataclass


@dataclass
class BadUserDTO:
    """Missing all parameters."""

    user_id: int
    email: str


@dataclass(frozen=True)
class PartialUserDTO:
    """Missing slots and repr=False."""

    user_id: int
    email: str


@dataclass(slots=True)
class AlmostGoodDTO:
    """Missing frozen and repr=False."""

    user_id: int
