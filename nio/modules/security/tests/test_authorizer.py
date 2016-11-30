from nio.modules.security.authorizer import Authorizer, Unauthorized
from nio.testing.test_case import NIOTestCaseNoModules


class AuthorizerImpl(object):

    """ A simple authorizer implementation.

    This considers an authorization valid if the task and user are the
    same thing. Definitely not recommended for production
    """

    @classmethod
    def authorize(cls, user, task):
        if user != task:
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
        Authorizer.authorize("test", "test")

    def test_authorize_fail(self):
        """ Test that when an authorize fails it raises Unauthorized """
        with self.assertRaises(Unauthorized):
            Authorizer.authorize("test", "fail")
