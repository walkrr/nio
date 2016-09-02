from time import sleep

from nio.modules.scheduler.job import Job
from unittest.mock import MagicMock
from datetime import timedelta
from nio.testing.test_case import NIOTestCase


class Dummy(object):

    def __init__(self):
        self.foo_called = 0

    def foo(self, add=1):
        self.foo_called += add


class TestJob(NIOTestCase):

    """ These tests assume they are being run with the TestScheduler that
    allows jumping forward in time. """

    def setUp(self):
        super().setUp()
        self.job = None
        self.dummy = Dummy()

    def tearDown(self):
        if self.job is not None:
            self.job.cancel()
        super().tearDown()

    def test_run_once(self):
        method = MagicMock()
        self.job = Job(method, timedelta(milliseconds=1), False)
        sleep(0.05)
        method.assert_called_once_with()

    def test_run_repeatedly(self):
        self.job = Job(self.dummy.foo, timedelta(seconds=1), True)
        # jump forward in time a little more than 3 seconds
        self.job.jump_ahead(3.1)
        self.assertEqual(self.dummy.foo_called, 3)

    def test_run_with_args(self):
        self.job = Job(self.dummy.foo, timedelta(seconds=1), False, 2)
        # jump forward in time a little more than 1 second
        self.job.jump_ahead(1.1)
        self.assertEqual(self.dummy.foo_called, 2)

    def test_run_with_kwargs(self):
        self.job = Job(self.dummy.foo, timedelta(seconds=1), False, add=3)
        # jump forward in time a little more than 1 second
        self.job.jump_ahead(1.1)
        self.assertEqual(self.dummy.foo_called, 3)

    def test_cancel_job(self):
        self.job = Job(self.dummy.foo, timedelta(seconds=2), True)
        self.assertEqual(self.dummy.foo_called, 0)
        self.job.cancel()
        # jump forward in time
        self.job.jump_ahead(2.5)
        self.assertEqual(self.dummy.foo_called, 0)
