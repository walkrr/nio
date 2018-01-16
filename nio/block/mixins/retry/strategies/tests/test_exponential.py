from unittest.mock import patch
from nio.util.logging import get_nio_logger
from nio.block.mixins.retry.strategies.exponential import ExponentialBackoff
from nio.testing import NIOTestCase


class TestExponentialBackoff(NIOTestCase):

    def assert_next_retry_sleeps_for(self, strat, num_seconds):
        """Make sure that given a failure the block will sleep for some time"""
        sleep_path = 'nio.block.mixins.retry.strategies.exponential.sleep'
        with patch(sleep_path) as sleep:
            strat.request_failed(Exception())
            if strat.should_retry():
                strat.wait_for_retry()
            sleep.assert_called_once_with(num_seconds)

    def test_default(self):
        """Test the default behavior of the exponential backoff"""
        strat = ExponentialBackoff(
            logger=get_nio_logger('ExponentialTest'),
            max_retry=5,
            multiplier=1,
            indefinite=False,
        )
        # First failure should sleep for 1 second
        self.assert_next_retry_sleeps_for(strat, 1)
        # Second failure should sleep for 2 seconds
        self.assert_next_retry_sleeps_for(strat, 2)
        # Third failure should sleep for 3 seconds
        self.assert_next_retry_sleeps_for(strat, 4)
        # Success should reset, so next failure will be 1 second
        strat.request_succeeded()
        self.assert_next_retry_sleeps_for(strat, 1)

    def test_multiplier(self):
        """Test that we can multiply the number of seconds to sleep"""
        strat = ExponentialBackoff(
            logger=get_nio_logger('ExponentialTest'),
            max_retry=5,
            multiplier=3.14,
            indefinite=False,
        )
        # Execute 3 retries and make sure we multiply each time
        self.assert_next_retry_sleeps_for(strat, 3.14)
        self.assert_next_retry_sleeps_for(strat, 6.28)
        self.assert_next_retry_sleeps_for(strat, 12.56)
        self.assert_next_retry_sleeps_for(strat, 25.12)

    def test_indefinite(self):
        """Test that retries can happen indefinitely """
        strat = ExponentialBackoff(
            logger=get_nio_logger('ExponentialTest'),
            max_retry=4,
            multiplier=1,
            indefinite=True,
        )
        # Should count to three retries then keep trying, every 2**3 seconds
        self.assert_next_retry_sleeps_for(strat, 1)
        self.assert_next_retry_sleeps_for(strat, 2)
        self.assert_next_retry_sleeps_for(strat, 4)
        self.assert_next_retry_sleeps_for(strat, 8)
        self.assert_next_retry_sleeps_for(strat, 8)
        self.assert_next_retry_sleeps_for(strat, 8)

    def test_multiplied_indefinite(self):
        """Test that retries can happen indefinitely """
        strat = ExponentialBackoff(
            logger=get_nio_logger('ExponentialTest'),
            max_retry=3,
            multiplier=3,
            indefinite=True,
        )
        # Should count to three retries then keep trying, every 3*2**2 seconds
        self.assert_next_retry_sleeps_for(strat, 3)
        self.assert_next_retry_sleeps_for(strat, 6)
        self.assert_next_retry_sleeps_for(strat, 12)
        self.assert_next_retry_sleeps_for(strat, 12)
        self.assert_next_retry_sleeps_for(strat, 12)

    def test_max_retries(self):
        """Test that we can cap the number of retries"""
        strat = ExponentialBackoff(
            logger=get_nio_logger('ExponentialTest'),
            max_retry=2,
            multiplier=1,
            indefinite=False,
        )
        # Execute 3 retries, but make sure only the first two actually sleep
        self.assert_next_retry_sleeps_for(strat, 1)
        self.assert_next_retry_sleeps_for(strat, 2)
        # Last retry should return false and not sleep
        sleep_path = 'nio.block.mixins.retry.strategies.exponential.sleep'
        with patch(sleep_path) as sleep:
            strat.request_failed(Exception())
            self.assertFalse(strat.should_retry())
            sleep.assert_not_called()
