"""Bad example: module-level facades that only delegate to a class method."""


class UserService:
    """Service with class methods."""

    @staticmethod
    def get_user(user_id: int) -> int:
        """Return the user id."""
        return user_id


def get_user(user_id: int) -> int:
    """Delegate directly to a class method."""
    return UserService.get_user(user_id)


def get_user_from_new_instance(user_id: int) -> int:
    """Delegate through a freshly constructed instance."""
    return UserService().get_user(user_id)


def get_user_from_named_instance(user_id: int) -> int:
    """Delegate through an instance bound on the previous line."""
    service = UserService()
    return service.get_user(user_id)


def fire_user_lookup(user_id: int) -> None:
    """Delegate as a bare expression statement."""
    UserService.get_user(user_id)
