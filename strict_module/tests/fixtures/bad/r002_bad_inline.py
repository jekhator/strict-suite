"""Bad example: inline dict literals with 3+ string keys."""


def build_response_bad():
    """Bad: inline dict with 3+ keys."""
    response = {
        "status": "ok",
        "user_id": 123,
        "message": "success",
        "timestamp": "2025-01-01",
    }
    return response


def process_config():
    """Bad: inline dict literal with business-shape."""
    config = {
        "timeout": 30,
        "retries": 3,
        "host": "localhost",
    }
    return config
