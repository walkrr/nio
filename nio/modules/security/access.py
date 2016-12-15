"""

    API Security

    Provides utility methods to ensure access to protected resources

"""
import threading
from nio.modules.security import Authorizer, SecureTask
from nio.modules.security import User


def get_user():
    """ Provides current user

    In the chance that no current user is available, a 'Guest' user is returned
    """
    thread = threading.current_thread()
    return getattr(thread, "user", User())


def set_user(user):
    """ Sets current user
    """
    setattr(threading.current_thread(), "user", user)


def has_access(resource, permission):
    """ Finds out if current user has permission to access given resource
    """
    return Authorizer.is_authorized(get_user(),
                                    SecureTask(resource, permission))


def ensure_access(resource, permission):
    """ Ensures that current user has permission to access given resource

    Raises:
        Unauthorized: if the user has no permission to access given resource
    """
    Authorizer.authorize(get_user(), SecureTask(resource, permission))
