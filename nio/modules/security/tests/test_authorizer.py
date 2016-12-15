from nio.modules.security import SecureTask
from nio.modules.security.authorizer import Authorizer, Unauthorized
from nio.testing.test_case import NIOTestCaseNoModules


class AuthorizerImpl(object):

    """ A simple authorizer implementation.

    This considers an authorization valid if the task and user are the
    same thing. Definitely not recommended for production
    """

    @classmethod
    def authorize(cls, user, task):
        if user != 'user' or not isinstance(task, SecureTask) or \
           task.resource != 'resource' or task.permission != 'permission':
            raise Unauthorized()


class TestAuthorizer(NIOTestCaseNoModules):

    def setUp(self):
        super().setUp()
        Authorizer.proxy(AuthorizerImpl)

    def tearDown(self):
        Authorizer.unproxy()
        super().tearDown()

    def test_authorize_pass(self):
        """ Test that a valid authorize passes """
        user = "user"
        task = SecureTask("resource", "permission")
        Authorizer.authorize(user, task)
        self.assertTrue(Authorizer.is_authorized(user, task))

    def test_authorize_fail(self):
        """ Test that when an authorize fails it raises Unauthorized """
        user = "u"
        task = SecureTask("r", "p")
        with self.assertRaises(Unauthorized):
            Authorizer.authorize(user, task)
            self.assertFalse(Authorizer.is_authorized(user, task))
