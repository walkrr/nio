"""
  Test testing functionality

"""
from datetime import datetime, timedelta
from threading import Event
from unittest import TestCase

from nio.testing.condition import ConditionWaiter, ensure_condition


class TestConditionWaiter(TestCase):
    def test_condition_waiter(self):
        """ Asserts that testing class works as expected, this does not
        test a NIO functionality.
        """

        class Holder(object):
            def __init__(self, start_value, max_value):
                self.value = start_value
                self.max_value = max_value
                self.num_calls = 0

        def my_check(holder):
            holder.num_calls += 1
            if holder.value == holder.max_value:
                return True
            holder.value += 1

        holder = Holder(1, 10)
        event = Event()
        condition = ConditionWaiter(event, my_check, holder)
        condition.start()
        self.assertTrue(event.wait(2))
        condition.stop()
        self.assertEqual(holder.num_calls, 10 - 1 + 1)

        holder = Holder(4, 10)
        event = Event()
        condition = ConditionWaiter(event, my_check, holder)
        condition.start()
        self.assertTrue(event.wait(3))
        condition.stop()
        self.assertEqual(holder.num_calls, 10 - 4 + 1)

        holder = Holder(1, 10)
        event = Event()
        condition = ConditionWaiter(event, my_check, holder)
        condition.start()
        self.assertFalse(event.wait(0.0001))
        condition.stop()

    def test_ensure_condition(self):

        def time_elapsed(start_time, elapsed_time):
            return (datetime.now() - start_time) > elapsed_time

        start_time = datetime.now()
        elapsed_time = timedelta(seconds=0.01)
        ensure_condition(time_elapsed, start_time, elapsed_time)
