from nio.testing.block.test_block import _TestBlock
from nio.signal.base import Signal
from nio.testing.block import NIOBlockTestCase
from nio.util.threading import spawn


class TestWaitForSignalsNotified(NIOBlockTestCase):

    @property
    def block_type(self):
        return _TestBlock

    def test_wait_for_signals_notified(self):
        """ Tests signals_notified when Block defines no output
        """
        self.configure_block({})
        self.start_block()

        # show that when nothing is notified
        with self.assertRaises(AssertionError):
            self.wait_for_signals_notified(wait_timeout_interval=0.01)
        with self.assertRaises(AssertionError):
            self.wait_for_signals_notified(wait_timeout_interval=0.01, count=1)

        # process signals on default input
        signal = Signal({"name": "s1"})
        self.process_signals([signal])

        # this wait passes since signals were just notified
        self.wait_for_signals_notified()
        self.assertEqual(len(self.signals_notified()), 1)

        self.reset_signals_notified()
        # assert than next wait should take into account new notifications
        with self.assertRaises(AssertionError):
            self.wait_for_signals_notified(wait_timeout_interval=0.01)
        with self.assertRaises(AssertionError):
            self.wait_for_signals_notified(wait_timeout_interval=0.01, count=1)

        # process three signals and wait
        self.process_signals([signal, signal, signal])
        self.wait_for_signals_notified(count=3)
        self.assertEqual(len(self.signals_notified()), 3)

        # process three signals and wait for two
        self.process_signals([signal, signal, signal])
        self.wait_for_signals_notified(count=2)

        self.reset_signals_notified()
        # assert than next wait should take into account new notifications
        with self.assertRaises(AssertionError):
            self.wait_for_signals_notified(wait_timeout_interval=0.01)
        with self.assertRaises(AssertionError):
            self.wait_for_signals_notified(wait_timeout_interval=0.01, count=1)

        # spawn a wait and process a signal
        t = spawn(self.wait_for_signals_notified, count=1)
        self.process_signals([signal])
        t.join()

        # spawn a wait for two and process two signals
        t = spawn(self.wait_for_signals_notified, count=2)
        self.process_signals([signal, signal])
        t.join()

        self.reset_signals_notified()
        # spawn a wait for two and process a single signal
        with self.assertRaises(AssertionError):
            t = spawn(self.wait_for_signals_notified(
                count=2, wait_timeout_interval=0.01))
            self.process_signals([signal])
            t.join()

        self.stop_block()
