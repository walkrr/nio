from nio.modules.proxy import ModuleProxy


class Unauthorized(Exception):

    """ Unauthorized security Exception

    Exception triggered when a user is not authorized to perform a task
    """
    pass


class Authorizer(ModuleProxy):

    @classmethod
    def authorize(cls, user, task):
        """ Ensure a user can perform a task.

        Args:
            user (User): A user object, likely returned by the Authenticator
            task (SecureTask): A task this user can or cannot perform

        Returns:
            None: The method will pass successfully if the user is authorized

        Raises:
            Unauthorized: if the user cannot perform the specified task
        """
        raise NotImplementedError()

    @classmethod
    def is_authorized(cls, user, task):
        """ Finds out if user can perform a task.

        Args:
            user (User): A user object, likely returned by the Authenticator
            task (SecureTask): A task this user can or cannot perform

        Returns:
            True: if user can perform the specified task
            False: otherwise
        """
        try:
            cls.authorize(user, task)
            return True
        except Unauthorized:
            return False
