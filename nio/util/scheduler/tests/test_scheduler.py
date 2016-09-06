from time import sleep
from threading import RLock
from unittest.mock import patch
from datetime import timedelta
from nio.modules.context import ModuleContext
from nio.util.scheduler.scheduler import SchedulerRunner
from nio.testing.test_case import NIOTestCaseNoModules
from nio.util.threading import spawn


class TestScheduler(NIOTestCaseNoModules):

    def setUp(self):
        super().setUp()
        self._scheduler = SchedulerRunner()
        ctx = ModuleContext()
        ctx.min_interval = 0.01
        ctx.resolution = 0.01
        self._scheduler.do_configure(ctx)
        self._scheduler.do_start()
        self._fired_times_lock = RLock()
        self.fired_times = 0

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

        sleep(interval.total_seconds() + self._scheduler._sched_resolution)
        self.assertEquals(self.fired_times, 1)

        sleep(interval.total_seconds())
        self.assertEquals(self.fired_times, 2)

        # make sure after cancelling, it is not firing any longer
        result = self._scheduler.unschedule(ev1)
        self.assertEquals(result, True)

        sleep(interval.total_seconds())
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
        assert False

    def test_min_interval(self):
        """ Asserts that a minimal interval is expected """
        self._scheduler.schedule_task(
            self._test_fired_times_callback,
            timedelta(seconds=0.0001),
            repeatable=True)
        # sleep more than min interval
        sleep(0.05)
        # with such a small timedelta (0.0001) jthe ob is expected in theory
        # to execute 100s of times, so asserting that it fired less than 10
        # times shows that a min_interval overwrote the timedelta
        self.assertGreater(self.fired_times, 0)
        self.assertLess(self.fired_times, 10)

    def test_min_interval_non_repeatable(self):
        """ Asserts that it is ok to pass a small time when not repeatable """
        self._scheduler.schedule_task(
            self._test_fired_times_callback,
            timedelta(seconds=0.0001),
            repeatable=False)
        sleep(0.05)
        self.assertEquals(self.fired_times, 1)

    def test_execute_pending_tasks(self):
        """ Asserts that multiple async calls to _execute_pending_tasks

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

        sleep(max_interval.total_seconds() + self._scheduler._sched_resolution)

        # assert ten tasks executed
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
