"""Bad example: validators not using DTO.from_dict() pattern."""


def validate_user_old_way(payload: dict) -> bool:
    """Bad: uses shape helpers instead of DTO.from_dict()."""
    if payload.get("user_id") and payload.get("email"):
        return True
    return False


def validate_config_loose(payload: dict) -> bool:
    """Bad: loose validation without proper pattern."""
    return "timeout" in payload and "host" in payload


def check_request_payload(payload: dict) -> None:
    """Bad: no DTO.from_dict() or ValidationError."""
    print(f"Checking: {payload}")
