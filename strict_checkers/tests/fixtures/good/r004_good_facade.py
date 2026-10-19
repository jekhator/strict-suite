"""Good example: tagged framework wrappers, module-level helpers with logic, and classes."""


class Mailer:
    """Send mail."""

    @staticmethod
    def send(recipient: str, subject: str) -> str:
        """Return a summary line."""
        return f"{recipient}: {subject}"


def async_send_email(recipient: str, subject: str) -> str:  # facade - celery schedule
    """Send email asynchronously via Celery."""
    return Mailer.send(recipient, subject)


def django_middleware_hook(request: object) -> object:  # FRAMEWORK
    """Django middleware hook function."""
    return request


def send_tagged_in_docstring(recipient: str) -> str:
    """Facade - Celery Schedule: transient event wrapper."""
    return Mailer.send(recipient, "tagged")


def format_total(values: list[int]) -> str:
    """Summarise a list of values."""
    total = sum(values)
    return f"total={total}"


class ServiceClass:
    """Non-facade service class."""

    def process_user(self, user_id: int) -> int:
        """Instance methods don't need tags."""
        return user_id
