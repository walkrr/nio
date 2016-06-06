from time import sleep
from threading import Event
from unittest.mock import MagicMock
from nio.block.base import Block
from nio.testing.block_test_case import NIOBlockTestCase
from nio.block.mixins.retry.retry import Retry
from nio.block.mixins.retry.strategy import BackoffStrategy
from nio.util.threading import spawn


class SleepBackoffStrategy(BackoffStrategy):
    """ A backoff strategy that sleeps """

    def __init__(self, sleep_time):
        super().__init__()
        self._sleep_time = sleep_time

    def should_retry(self):
        return True

    def wait_for_retry(self):
        sleep(self._sleep_time)


class RetryingBlock(Retry, Block):

    def __init__(self, sleep_retry_time):
        super().__init__()
        self._sleep_time = sleep_retry_time

    def setup_backoff_strategy(self):
        self.use_backoff_strategy(SleepBackoffStrategy, self._sleep_time)


class TestCancelRetry(NIOBlockTestCase):

    def test_stop_loop(self):
        """Tests that the retry mixin loop can be stopped/cancelled"""
        block = RetryingBlock(0.01)
        self.configure_block(block, {})
        # Target func will fail twice, then return a number
        target_func = MagicMock(side_effect=[Exception, Exception,
                                             Exception, "Success"])

        stop_retry_event = Event()
        execute_thread = spawn(block.execute_with_retry, target_func,
                               stop_retry_event=stop_retry_event)
        sleep(0.01)
        stop_retry_event.set()
        result = execute_thread.join()

        # no result it exited through loop end
        self.assertIsNone(result)
        # assert target was called more than once and that it was interrupted
        self.assertGreater(target_func.call_count, 0)
        self.assertLess(target_func.call_count, 4)
