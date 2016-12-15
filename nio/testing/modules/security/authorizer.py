from nio.modules.security import User
from nio.modules.security.task import SecureTask
from nio.modules.security.authorizer import Unauthorized


class Authorizer(object):

    @classmethod
    def authorize(cls, user, task):
        if not isinstance(user, User) or not isinstance(task, SecureTask):
            raise Unauthorized()
