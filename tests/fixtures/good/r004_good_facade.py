"""Good example: module-level functions with exception tags."""


def async_send_email(recipient: str, subject: str):  # facade — celery schedule
    """Send email asynchronously via Celery."""
    pass


def django_middleware_hook(request):  # FRAMEWORK
    """Django middleware hook function."""
    return request


class ServiceClass:
    """Non-facade service class."""

    def process_user(self, user_id: int):
        """Instance methods don't need tags."""
        pass
