from nio.testing.block.test_block import _TestBlock
from nio.signal.base import Signal
from nio.signal.status import BlockStatusSignal
from nio.util.runner import RunnerStatus
from nio.testing.block import NIOBlockTestCase


class TestSignalsNotifications(NIOBlockTestCase):

    @property
    def block_type(self):
        """ Overrides block_type to use for all tests
        """
        return _TestBlock

    def test_allows_signal_notify(self):
        """ Makes sure a test can assert how many signals were notified """
        self.configure_block({})
        self.start_block()

        self.process_signals([Signal(), Signal()])

        # Assert that 2 total signals were captured
        self.assert_num_signals_notified(2)

        self.stop_block()

    def test_allows_mgmt_signal_notify(self):
        """ Makes sure a test can assert how many mgmt signals were notified """
        self.configure_block({})
        self.start_block()

        # First make sure block has no status
        self.assert_block_status('')

        self.notify_management_signal(BlockStatusSignal(RunnerStatus.error))

        # assert new block status
        self.assert_block_status(RunnerStatus.error)
        # assert that 1 total signal was captured
        self.assert_num_mgmt_signals_notified(1)

        self.stop_block()

    def test_event_notification(self):
        """ Makes sure test can can wait on 'signals_notified_event' """
        self.configure_block({})
        self.start_block()

        self.assertFalse(self.signals_notified_event.is_set())
        self.process_signals([Signal(), Signal()])
        self.assertTrue(self.signals_notified_event.wait(0.001))

        self.stop_block()
