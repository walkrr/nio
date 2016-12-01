import threading
from unittest.mock import patch

from nio.modules.security.access import ensure_access
from nio.modules.security import Authorizer
from nio.modules.security import Unauthorized
from nio.testing.test_case import NIOTestCase
from nio.modules.security.task import SecureTask
from nio.modules.security.user import User


class SecuredClass(object):

    def __init__(self, *tasks):
        self.went_through = False
        self._tasks = tasks

    def secured_method(self):
        ensure_access(*self._tasks)
        self.went_through = True


class TestAccess(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'security'}

    def test_access(self):
        """ Ensures authorize is called and results are handled as expected """

        secured_class = SecuredClass("test", "secured_method", "write")

        # class must have a 'commands' attribute
        with patch.object(Authorizer, "authorize", side_effect=Unauthorized):
            with self.assertRaises(Unauthorized):
                secured_class.secured_method()

        # check authorize arguments
        user = User()
        setattr(threading.current_thread(), "user", user)
        with patch.object(Authorizer, "authorize") as mocked_authorize:
            secured_class.secured_method()

            # assert right user was provided
            self.assertEqual(user, mocked_authorize.call_args[0][0])
            # assert type
            self.assertIsInstance(mocked_authorize.call_args[0][1], SecureTask)
            # assert task composition
            self.assertEqual("test.secured_method.write",
                             mocked_authorize.call_args[0][1].task)
