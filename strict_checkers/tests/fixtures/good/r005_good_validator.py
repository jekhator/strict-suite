"""Good example: validators using DTO.from_dict() pattern."""

from dataclasses import dataclass

import constants as const  # type: ignore[import-not-found]


@dataclass(frozen=True, slots=True, repr=False)
class UserDTO:
    """User DTO."""

    user_id: int
    email: str


class ValidationError(Exception):
    """Validation error."""

    pass


def validate_user_payload(payload: dict) -> UserDTO:  # module-level: fixture helper with no owning class
    """Good: uses DTO.from_dict() for shape validation."""
    try:
        user = UserDTO(
            user_id=payload["user_id"],
            email=payload["email"],
        )
        return user
    except (KeyError, TypeError) as error:
        raise ValidationError(const.ERR_PAYLOAD_INVALID)


def validate_config(payload: dict) -> bool:  # module-level: fixture helper with no owning class
    """Good: raises ValidationError on invalid shape."""
    if "timeout" not in payload:
        raise ValidationError(const.ERR_TIMEOUT_MISSING)
    return True
