from datetime import timedelta

from nio.modules.scheduler.job import Job
from nio.testing.condition import ensure_condition
from nio.testing.test_case import NIOTestCase

arg1_parameter = "8"
kwarg1_parameter = "kwarg1_replacement"


class Dummy(object):

    def __init__(self, test_case):
        self.foo1_called = False
        self.test_case = test_case

    def foo1(self, arg1, kwarg1='kwarg1'):
        self.foo1_called = True
        self.test_case.assertEquals(arg1, arg1_parameter)
        self.test_case.assertEquals(kwarg1, kwarg1_parameter)


class TestScheduler(NIOTestCase):

    def test_args(self):
        """ Asserts that scheduler accepts args and kwargs """
        dummy = Dummy(self)
        self.job1 = Job(dummy.foo1, timedelta(milliseconds=1), False,
                        arg1_parameter, kwarg1=kwarg1_parameter)
        self.job1.jump_ahead(5)
        ensure_condition(self._foo_called, dummy)
        self.assertEqual(dummy.foo1_called, True)

    def _foo_called(self, dummy):
        return dummy.foo1_called
