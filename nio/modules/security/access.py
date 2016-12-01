"""

    API Security

    Provides utility methods to ensure access to protected resources

"""
import threading
from nio.modules.security import Authorizer, SecureTask


def get_user():
    """ Provides current logged in user
    """
    thread = threading.current_thread()
    return getattr(thread, "user", None)


def ensure_access(*task_parts):
    """ Ensures access to resource is granted

    Usage:
        ensure_access("services", "Service1", "read")
        ensure_access("services", "Service1", "write")
        ensure_access("services", "Service1", "execute")
        ensure_access("instance", "execute")

    Raises:
        Unauthorized: access is denied
    """
    task = ".".join(task_parts)
    Authorizer.authorize(get_user(), SecureTask(task))
