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
