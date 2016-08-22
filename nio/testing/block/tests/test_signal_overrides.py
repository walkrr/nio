from nio.testing.block.tests.block import _TestBlock
from nio.signal.base import Signal
from nio.signal.status import BlockStatusSignal
from nio.util.runner import RunnerStatus
from nio.testing.block import NIOBlockTestCase


class TestSignalOverrides(NIOBlockTestCase):

    @property
    def block_type(self):
        """ Overrides block_type to use for all tests
        """
        return _TestBlock

    def on_signals_notified(self, signals, output_id):
        """ Override a signal notification handler """
        self._signals_notified_override = True

    def on_management_signal_notified(self, signal):
        """ Override a management signal notification handler """
        self._management_notified_override = True
        self.assertEqual(signal.block_name, self.block.name())
        self.assertEqual(signal.service_name, self.block._service_name)

    def test_allows_signal_handler_override(self):
        """ Makes sure a test can override a signal handler """
        self._signals_notified_override = False
        self.configure_block({})
        self.start_block()

        self.assertFalse(self._signals_notified_override)
        self.process_signals([Signal()])
        self.assertTrue(self._signals_notified_override)

        self.stop_block()

    def test_allows_mgmt_signal_handler_override(self):
        """ Makes sure a test can override a management signal handler """
        self._management_notified_override = False
        self.configure_block({})
        self.start_block()

        self.assertFalse(self._management_notified_override)
        self.notify_management_signal(BlockStatusSignal(RunnerStatus.error))
        self.assertTrue(self._management_notified_override)

        self.stop_block()
