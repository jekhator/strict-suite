"""Good example: no Dict[str, Any] in service signatures."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, repr=False)
class UserDTO:
    """User data transfer object."""

    user_id: int
    email: str


def process_user(user_id: int) -> UserDTO:  # FRAMEWORK
    """Process a user without Dict[str, Any]."""
    return UserDTO(user_id=user_id, email="test@example.com")


class UserValidator:
    """User validator (no tags needed for instance methods)."""

    def validate_user(self, user: UserDTO) -> bool:
        """Validate user object."""
        return bool(user.email)


def create_user_response(user: UserDTO) -> dict:  # facade — celery schedule
    """Return user as dict (OK at boundary)."""
    return {"id": user.user_id, "email": user.email}
