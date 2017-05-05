from datetime import timedelta
from threading import RLock
from unittest.mock import patch

from nio.modules.context import ModuleContext
from nio.testing.condition import ensure_condition
from nio.testing.modules.scheduler.scheduler import JumpAheadSchedulerRunner
from nio.testing.test_case import NIOTestCaseNoModules
from nio.util.threading import spawn


class TestScheduler(NIOTestCaseNoModules):

    def setUp(self):
        super().setUp()
        self._scheduler = JumpAheadSchedulerRunner()
        ctx = ModuleContext()
        ctx.min_interval = 0.01
        ctx.resolution = 0.01
        self._scheduler.do_configure(ctx)
        self._scheduler.do_start()
        self._fired_times_lock = RLock()
        self._fired_times = 0

    def tearDown(self):
        self._scheduler.do_stop()
        super().tearDown()

    def test_add_and_cancel(self):
        """ Asserts that a repeatable scheduling actually repeats.

        This means is called at least two times and after it is cancelled no
        more calls are issued
        """

        interval = timedelta(seconds=0.02)
        ev1 = self._scheduler.schedule_task(
            self._test_fired_times_callback, interval, repeatable=True)

        self._scheduler.jump_ahead(interval.total_seconds() +
                                   self._scheduler._sched_resolution)
        ensure_condition(self._check_fired_times, 1)
        self.assertEquals(self.fired_times, 1)

        self._scheduler.jump_ahead(interval.total_seconds())
        ensure_condition(self._check_fired_times, 2)
        self.assertEquals(self.fired_times, 2)

        # make sure after cancelling, it is not firing any longer
        self.assertTrue(self._scheduler.unschedule(ev1))
        # do another jump and verify no triggering
        self._scheduler.jump_ahead(interval.total_seconds())
        self.assertEquals(self.fired_times, 2)

    def _test_fired_times_callback(self):
        self.fired_times += 1

    def test_invalid_time(self):
        """ Asserts that an invalid time data type is not allowed """

        with self.assertRaises(AttributeError):
            self._scheduler.schedule_task(
                self._test_invalid_time_callback, 11, repeatable=True)

    def _test_invalid_time_callback(self):
        # should not come here, assert otherwise
        raise ValueError()

    def test_min_interval(self):
        """ Asserts that a minimal interval is expected """
        self._scheduler.schedule_task(
            self._test_fired_times_callback,
            timedelta(seconds=0.0001),
            repeatable=True)
        # jump more than min interval
        self._scheduler.jump_ahead(0.05)
        # with such a small timedelta (0.0001) the job is expected in theory
        # to execute 100s of times, so asserting that it fired less than 10
        # times shows that a min_interval overwrote the timedelta
        ensure_condition(self._check_fired_times_greater_than, 0)
        self.assertGreater(self.fired_times, 0)
        ensure_condition(self._check_fired_times_less_than, 10)
        self.assertLess(self.fired_times, 10)

    def test_min_interval_non_repeatable(self):
        """ Asserts that it is ok to pass a small time when not repeatable """
        self._scheduler.schedule_task(
            self._test_fired_times_callback,
            timedelta(seconds=0.0001),
            repeatable=False)
        self._scheduler.jump_ahead(0.05)
        ensure_condition(self._check_fired_times, 1)
        self.assertEquals(self.fired_times, 1)

    def test_execute_pending_tasks(self):
        """ Asserts multiple async calls to _execute_pending_tasks

        Launches a number of async calls to '_execute_pending_tasks', which
        will execute along with the '_process_events' loop, asserting that
        results are as expected
        """
        delta = 0.02
        max_interval = timedelta(seconds=delta)
        threads = []
        for i in range(1, 11):
            self._scheduler.schedule_task(
                self._test_fired_times_callback,
                timedelta(seconds=delta * i / 10),
                repeatable=False)
            # launch async this method and make sure it causes no side effects
            threads.append(spawn(self._scheduler._execute_pending_tasks))

        # wait for all _execute_pending_tasks to finish
        for thread in threads:
            thread.join(1)
            self.assertFalse(thread.is_alive())

        self._scheduler.jump_ahead(max_interval.total_seconds() +
                                   self._scheduler._sched_resolution)

        # assert ten tasks executed
        ensure_condition(self._check_fired_times, 10)
        self.assertEquals(self.fired_times, 10)

        # assert internal collections are empty
        self.assertEqual(len(self._scheduler._queue), 0)
        self.assertEqual(len(self._scheduler._events), 0)

        # assert loop is still going
        self.assertFalse(self._scheduler._stop_event.is_set())

    @property
    def fired_times(self):
        with self._fired_times_lock:
            return self._fired_times

    @fired_times.setter
    def fired_times(self, times):
        with self._fired_times_lock:
            self._fired_times = times

    def test_invalid_cancel(self):
        """ Asserts that trying to cancel an invalid job returns False """
        event_id = self._scheduler.schedule_task(
            self._test_fired_times_callback,
            timedelta(seconds=0.1),
            repeatable=True)
        self.assertFalse(self._scheduler.unschedule("invalid_id"))

        with patch('heapq.heapify',
                   side_effect=Exception("Patch induced exception")):
            self.assertFalse(self._scheduler.unschedule(event_id))

    def _check_fired_times(self, times):
        return self.fired_times == times

    def _check_fired_times_greater_than(self, times):
        return self.fired_times > times

    def _check_fired_times_less_than(self, times):
        return self.fired_times < times
