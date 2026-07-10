"""Good example: few dict keys or proper DTO usage."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, repr=False)
class ConfigDTO:
    """Config data transfer object."""

    timeout: int
    retries: int
    host: str


def build_config() -> ConfigDTO:
    """Build config using DTO."""
    return ConfigDTO(timeout=30, retries=3, host="localhost")


def simple_dict() -> dict:
    """Simple dict with 1-2 keys is OK."""
    return {"status": "ok"}


def create_response(ok: bool) -> dict:
    """Return simple dict at boundary."""
    return {"success": ok}
