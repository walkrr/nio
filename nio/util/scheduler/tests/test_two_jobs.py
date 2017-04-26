from datetime import timedelta

from nio.modules.scheduler.job import Job
from nio.testing.condition import ensure_condition
from nio.testing.test_case import NIOTestCase


class Dummy(object):

    def __init__(self):
        self.foo1_called = False
        self.foo2_called = False

    def foo1(self):
        self.foo1_called = True

    def foo2(self):
        self.foo2_called = True


class TestScheduler(NIOTestCase):

    def _foo1_called(self, dummy):
        return dummy.foo1_called, True

    def _foo2_called(self, dummy):
        return dummy.foo2_called, True

    def test_two_jobs(self):
        """ Asserts that the right task is executed first """
        dummy = Dummy()
        self.job1 = Job(dummy.foo1, timedelta(milliseconds=500), False)
        self.job2 = Job(dummy.foo2, timedelta(milliseconds=200), False)
        # simulate a jump forward in time
        self.job1.jump_ahead(0.8)
        ensure_condition(self._foo1_called, dummy)
        ensure_condition(self._foo2_called, dummy)

    def test_two_jobs_reverse_order(self):
        """ Asserts that the right task is executed first

        This is the  same as above test but calls are reversed
        """
        dummy = Dummy()
        self.job2 = Job(dummy.foo2, timedelta(milliseconds=100), False)
        self.job1 = Job(dummy.foo1, timedelta(milliseconds=500), False)
        # simulate a jump forward in time
        self.job1.jump_ahead(0.8)
        ensure_condition(self._foo1_called, dummy)
        ensure_condition(self._foo2_called, dummy)
