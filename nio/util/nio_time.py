from datetime import datetime


def get_nio_time():
    """ Generate a nicely formatted ISO 8601 time string for a log entry

    Returns:
        ISO 8601-conformant time string
    """
    return datetime.utcnow().isoformat() + "Z"
