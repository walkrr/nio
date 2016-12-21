from nio.block.terminals import input, output
from nio.signal.base import Signal
from nio.testing.block import NIOBlockTestCase
from nio.testing.block.tests.block import _TestBlock


class TestResetDefaultTerminal(NIOBlockTestCase):

    @property
    def block_type(self):
        return _TestBlock

    def test_signals_default_terminal(self):
        """ Tests reset_signals_notified when Block defines no output
        """
        self.configure_block({})
        self.start_block()

        # process signals on default output
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        # don't specify any output
        self.process_signals([default_output_signal1, default_output_signal2])

        # grab signals notified
        signals_notified = self.signals_notified()
        self.assertIn(default_output_signal1, signals_notified)
        self.assertIn(default_output_signal2, signals_notified)

        # reset signals
        self.reset_signals_notified()
        # get signals again and verify that signals are not in
        signals_notified = self.signals_notified()
        self.assertNotIn(default_output_signal1, signals_notified)
        self.assertNotIn(default_output_signal2, signals_notified)

        # reset signals on not-existent named output raises an exception
        with self.assertRaises(ValueError):
            self.reset_signals_notified("output1")

        self.stop_block()


@input("input1")
@output("output1")
class BlockWithOutput(_TestBlock):
    pass


class TestResetBlockWithOutput(NIOBlockTestCase):

    @property
    def block_type(self):
        return BlockWithOutput

    def test_reset_signals_notified(self):
        """ Tests reset_signals_notified on a Block with outputs but no default
        """
        self.configure_block({})
        self.start_block()

        # process signals on named inputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.process_signals([output1_signal1, output1_signal2], "input1")

        # assert signals notified
        signals_notified = self.signals_notified()
        self.assertIn(output1_signal1, signals_notified)
        self.assertIn(output1_signal2, signals_notified)

        # reset signals on named output
        self.reset_signals_notified("output1")
        # get signals again and verify that signals are not in
        signals_notified = self.signals_notified("output1")
        self.assertNotIn(output1_signal1, signals_notified)
        self.assertNotIn(output1_signal2, signals_notified)

        self.stop_block()
