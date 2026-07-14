"""Good: Module-level functions that are allowed entry points."""


def main(args):
    """Main entry point is allowed."""
    service = ServiceClass()
    return service.process(args)


def handle_command(cmd):
    """handle_command entry point is allowed."""
    return cmd.execute()


def handle_event(event):
    """handle_event entry point is allowed."""
    return event.process()


def handle_request(request):
    """handle_request entry point is allowed."""
    return request.handle()


def handle_webhook(data):
    """handle_* pattern is allowed."""
    return data.webhook()


class ServiceClass:
    """All non-entry-point logic lives in classes."""

    def process(self, data):
        """Process data."""
        return data.upper()

    def calculate_sum(self, a, b):
        """Calculate sum."""
        return a + b
