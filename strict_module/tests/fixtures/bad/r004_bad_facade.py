"""Bad example: module-level functions without exception tags."""


def bare_process_user(user_id: int):
    """No exception tag for module-level function."""
    return {"id": user_id}


def another_helper(config):
    """Another bare function without tag."""
    pass


def third_function():
    """Third bare function without tag."""
    pass
