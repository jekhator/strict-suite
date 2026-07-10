"""Good example: validators using DTO.from_dict() pattern."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, repr=False)
class UserDTO:
    """User DTO."""

    user_id: int
    email: str


class ValidationError(Exception):
    """Validation error."""

    pass


def validate_user_payload(payload: dict) -> UserDTO:
    """Good: uses DTO.from_dict() for shape validation."""
    try:
        user = UserDTO(
            user_id=payload["user_id"],
            email=payload["email"],
        )
        return user
    except (KeyError, TypeError) as e:
        raise ValidationError(f"Invalid payload: {e}")


def validate_config(payload: dict) -> bool:
    """Good: raises ValidationError on invalid shape."""
    if "timeout" not in payload:
        raise ValidationError("Missing timeout")
    return True
