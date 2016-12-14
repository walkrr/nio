from unittest.mock import patch

from nio.modules.security.access import ensure_access, has_access, set_user
from nio.modules.security import Authorizer
from nio.modules.security import Unauthorized
from nio.testing.test_case import NIOTestCase
from nio.modules.security.task import SecureTask
from nio.modules.security.user import User


class SecuredClass(object):

    def __init__(self, resource, permission, test_case):
        self._resource = resource
        self._permission = permission
        self._test_case = test_case

    def secured_method(self):
        ensure_access(self._resource, self._permission)
        # assert that if access was granted then user has access
        self._test_case.assertTrue(has_access(self._resource, self._permission))


class TestAccess(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'security'}

    def test_access(self):
        """ Ensures authorize is called and results are handled as expected """

        secured_class = SecuredClass("resource", "permission", self)

        with patch.object(Authorizer, "authorize", side_effect=Unauthorized):
            with self.assertRaises(Unauthorized):
                secured_class.secured_method()

        # check authorize arguments
        user = User()
        set_user(user)
        with patch.object(Authorizer, "authorize") as mocked_authorize:

            # invoke actual secure method
            secured_class.secured_method()

            # assert right user was provided
            self.assertEqual(user, mocked_authorize.call_args[0][0])
            # assert type
            self.assertIsInstance(mocked_authorize.call_args[0][1], SecureTask)
            # assert resource and permission arguments to authorize
            self.assertEqual("resource",
                             mocked_authorize.call_args[0][1].resource)
            self.assertEqual("permission",
                             mocked_authorize.call_args[0][1].permission)
