from copy import copy
from unittest.mock import patch

from nio.block.base import Block
from nio.block.terminals import DEFAULT_TERMINAL, output
from nio.signal.base import Signal
from nio.signal.status import BlockStatusSignal
from nio.util.runner import RunnerStatus
from nio.testing.block_test_case import NIOBlockTestCase


class TestBlockTestCase(NIOBlockTestCase):

    """ Tests that the BlockTestCase handles router methods properly. """

    def signals_notified(self, block, signals, output_id=DEFAULT_TERMINAL):
        """ Override a signal notification handler """
        self._signals_notified = True
        super().signals_notified(block, signals, output_id)

    def management_signal_notified(self, signal):
        """ Override a management signal notification handler """
        # allow mgmt signal counting
        super().management_signal_notified(signal)
        # make it known that it was notified
        self._management_notified = True

    def test_allows_signal_notify(self):
        """ Makes sure a test can assert how many signals were notified """
        b1 = Block()
        b2 = Block()
        self.configure_block(b1, {})
        self.configure_block(b2, {})

        b1.notify_signals([Signal(), Signal()])
        b2.notify_signals([Signal()])

        # Assert that 3 total signals were captured
        self.assert_num_signals_notified(3)

        # Assert that we captured the right number of signals per block too
        self.assert_num_signals_notified(2, b1)
        self.assert_num_signals_notified(1, b2)

    def test_allows_mgmt_signal_notify(self):
        """ Makes sure a test can assert how many mgmt sigs were notified """
        b1 = Block()
        b2 = Block()
        self.configure_block(b1, {})
        self.configure_block(b2, {})

        # First make sure our blocks have no status
        self.assert_block_status(b1, '')
        self.assert_block_status(b2, '')

        b1.notify_management_signal(BlockStatusSignal(RunnerStatus.error))
        self.assert_num_mgmt_signals_notified(1, b1)
        self.assert_num_mgmt_signals_notified(0, b2)

        b2.notify_management_signal(BlockStatusSignal(RunnerStatus.warning))
        self.assert_num_mgmt_signals_notified(1, b1)
        self.assert_num_mgmt_signals_notified(1, b2)

        # Assert that 2 total signals were captured
        self.assert_num_mgmt_signals_notified(2)

    def test_allows_mgmt_signal_handler_override(self):
        """ Makes sure a test can override a management signal handler """
        self._management_notified = False
        b1 = Block()
        self.configure_block(b1, {})

        self.assertFalse(self._management_notified)
        b1.notify_management_signal(BlockStatusSignal(RunnerStatus.error))
        self.assertTrue(self._management_notified)

    def test_allows_signal_handler_override(self):
        """ Makes sure a test can override a signal handler """
        self._signals_notified = False
        b1 = Block()
        self.configure_block(b1, {})

        self.assertFalse(self._signals_notified)
        b1.notify_signals([Signal()])
        self.assertTrue(self._signals_notified)

    def test_invalid_output(self):
        """ Asserts that no exception is raised when output is invalid.

        This is an intentionally added feature added to the block unit test
        to prevent test writers from having to explicitly have to add outputs
        to testing blocks if they want to notify signals to a different output.
        """
        b1 = Block()
        self.configure_block(b1, {})
        b1.notify_signals([Signal()], "invalid_output")
        self.assert_num_signals_notified(1, b1, "invalid_output")

    def test_last_signal_notified(self):
        """ Tests last_signal_notified functionality
        """
        b1 = Block()
        self.configure_block(b1, {})

        # notify signals on default output
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        b1.notify_signals([default_output_signal1, default_output_signal2])

        # notify signals on named outputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        b1.notify_signals([output1_signal1, output1_signal2], "output1")

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        b1.notify_signals([output2_signal1, output2_signal2], "output2")

        # assert which signal is returned when output is not specified
        self.assertEqual(self.last_signal_notified(), output2_signal2)

        # assert last signal for specified outputs
        self.assertEqual(self.last_signal_notified("output1"), output1_signal2)
        self.assertEqual(self.last_signal_notified("output2"), output2_signal2)
        self.assertEqual(
            self.last_signal_notified(DEFAULT_TERMINAL),
            default_output_signal2)

        # notify and assert that signal changed when no output is specified
        b1.notify_signals([default_output_signal1, default_output_signal2])
        self.assertEqual(self.last_signal_notified(), default_output_signal2)

        # assert that last signal for specified outputs remains the same
        self.assertEqual(self.last_signal_notified("output1"), output1_signal2)
        self.assertEqual(self.last_signal_notified("output2"), output2_signal2)
        self.assertEqual(
            self.last_signal_notified(DEFAULT_TERMINAL),
            default_output_signal2)

        # assert that when output is specified, it must be valid when getting
        # last signal from it
        with self.assertRaises(ValueError):
            self.assertEqual(self.last_signal_notified("INVALID_OUTPUT"),
                             default_output_signal2)

    def test_signal_notified(self):
        """ Tests assert_signal_notified functionality 
        """
        b1 = Block()
        self.configure_block(b1, {})
        signal = Signal({"hello": "n.io"})
        signal2 = Signal({"goodbye": "n.io"})

        b1.notify_signals([signal], DEFAULT_TERMINAL)
        b1.notify_signals([signal2], DEFAULT_TERMINAL)
        b1.notify_signals([signal], "output1")

        # assert output_id behavior
        self.assert_signal_notified(signal)
        self.assert_signal_notified(signal, output_id="output1")

        # assert position behavior
        self.assert_signal_notified(signal, position=0)
        with self.assertRaises(IndexError):
            self.assert_signal_notified(signal, position=2)
        self.assert_signal_notified(signal, position=0, output_id="output1")

        # assert wrong position raises exception
        with self.assertRaises(AssertionError):
            self.assert_signal_notified(signal2, position=0)

        # asserting a signal that hasn't been notified raises an exception
        with self.assertRaises(AssertionError):
            self.assert_signal_notified(Signal({"welcome back": "n.io"}))

    def test_signal_list_notified(self):
        """ Tests assert_signal_notified functionality 
        """
        b1 = Block()
        self.configure_block(b1, {})

        signal1 = Signal({"hello": "n.io"})
        signal2 = Signal({"goodbye": "n.io"})
        signal3 = Signal({"welcome back": "n.io"})
        signal4 = Signal({"do come back": "n.io"})

        b1.notify_signals([signal1, signal2], DEFAULT_TERMINAL)
        b1.notify_signals([signal2, signal3], DEFAULT_TERMINAL)
        b1.notify_signals([signal3, signal4], DEFAULT_TERMINAL)

        # list should be order-dependent
        self.assert_signal_list_notified([signal1, signal2])
        self.assert_signal_list_notified([signal3, signal4])
        self.assert_signal_list_notified([copy(signal3), copy(signal4)])
        self.assert_signal_list_notified([signal3, copy(signal4)])
        with self.assertRaises(AssertionError):
            self.assert_signal_list_notified([signal2, signal1])

        # assert position behavior
        self.assert_signal_list_notified([signal1, signal2], position=0)
        self.assert_signal_list_notified([signal3, signal4], position=2)

        # assert wrong position raises exception
        with self.assertRaises(AssertionError):
            self.assert_signal_list_notified([signal3, signal4], position=0)

        # lists that weren't notified but still have notified the same signals
        # should not work
        with self.assertRaises(AssertionError):
            self.assert_signal_list_notified([signal1, signal4])

        # sub-lists of the whole notified list should not work
        with self.assertRaises(AssertionError):
            self.assert_signal_list_notified([signal1])
            self.assert_signal_list_notified([signal2])

    def test_assert_last_signal_notified(self):
        """ Tests assert_last_signal_notified functionality 
        """
        b1 = Block()
        self.configure_block(b1, {})
        signal1 = Signal({"hello": "n.io"})
        signal2 = Signal({"goodbye": "n.io"})

        b1.notify_signals([signal1], DEFAULT_TERMINAL)
        self.assert_last_signal_notified(signal1)
        b1.notify_signals([signal2], DEFAULT_TERMINAL)
        self.assert_last_signal_notified(signal2)
        b1.notify_signals([signal1], DEFAULT_TERMINAL)
        self.assert_last_signal_notified(signal1)

        # test list behavior, the last signal in the list should be the last
        # signal notified
        b1.notify_signals([signal1, signal2], DEFAULT_TERMINAL)
        self.assert_last_signal_notified(signal2)

        with self.assertRaises(AssertionError):
            self.assert_last_signal_notified(signal1)

    def test_last_signal_list_notified(self):
        """ Tests assert_last_signal_list_notified functionality 
        """
        b1 = Block()
        self.configure_block(b1, {})
        signal1 = Signal({"hello": "n.io"})
        signal2 = Signal({"goodbye": "n.io"})

        # first list
        b1.notify_signals([signal1, signal2], DEFAULT_TERMINAL)
        self.assert_last_signal_list_notified([signal1, signal2])
        # list should be order-dependent
        with self.assertRaises(AssertionError):
            self.assert_last_signal_list_notified([signal2, signal1])

        # second list, the notified signals should reset automatically
        b1.notify_signals([signal2, signal1], DEFAULT_TERMINAL)
        self.assert_last_signal_list_notified([signal2, signal1])

    def test_block_default_output(self):
        """ Tests that a block with a default output uses it by default """

        @output('out1', default=True)
        @output('out2')
        class MyBlock(Block):
            pass

        blk = MyBlock()
        self.configure_block(blk, {})
        sig1, sig2, sig3 = (
            Signal({'sig': 1}),
            Signal({'sig': 2}),
            Signal({'sig': 3}),
        )
        blk.notify_signals([sig1], 'out1')
        self.assert_last_signal_notified(sig1, 'out1')
        blk.notify_signals([sig2], 'out2')
        self.assert_last_signal_notified(sig2, 'out2')
        # Notify the last signal without any output ID, make sure the actual
        # default terminal of the block is used
        blk.notify_signals([sig3])
        self.assert_last_signal_notified(sig3, 'out1')
