from collections import defaultdict

from nio.block.base import Block
from nio.block.terminals import DEFAULT_TERMINAL, input
from nio.signal.base import Signal
from nio.testing.block import NIOBlockTestCase


class ParentTestBlock(Block):
    def __init__(self):
        super().__init__()
        self._signals_processed = defaultdict(list)

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self._signals_processed[input_id].extend(signals)


@input("input1")
@input("input2")
class BlockWithInputs(ParentTestBlock):
    pass


@input("input1", default=True)
@input("input2")
class BlockWithDefaultInputSpecified(ParentTestBlock):
    pass


class TestProcessSignals(NIOBlockTestCase):

    def test_process_signals_default_terminal(self):
        """ Tests process_signals when no explicit input is defined
        """
        self.block_type = ParentTestBlock
        self.configure_block({})

        # process signals on default input
        default_input_signals = [Signal({"name": "default_s1"}),
                                 Signal({"name": "default_s2"})]
        self.process_signals(default_input_signals)

        # process signals on a named input is invalid
        input1_signals = [Signal({"name": "i1_s1"})]
        # input1 is invalid
        with self.assertRaises(ValueError):
            self.process_signals(input1_signals, "input1")

        # asserts signals are processed on right inputs
        self.assertEqual(self.block._signals_processed[DEFAULT_TERMINAL],
                         default_input_signals)
        self.assertNotIn("input1", self.block._signals_processed)

    def test_process_signals_no_default(self):
        """ Tests process_signals when inputs are defined but no default
        """
        self.block_type = BlockWithInputs
        self.configure_block({})

        # process signals on default input
        default_input_signals = [Signal({"name": "default_s1"}),
                                 Signal({"name": "default_s2"})]
        # this block has inputs defined but none of them marked as default
        with self.assertRaises(ValueError):
            self.process_signals(default_input_signals)

        # process signals on named inputs
        input1_signals = [Signal({"name": "i1_s1"}), Signal({"name": "i1_s2"})]
        self.process_signals(input1_signals, "input1")

        input2_signals = [Signal({"name": "i2_s1"}), Signal({"name": "i2_s2"})]
        self.process_signals(input2_signals, "input2")

        # asserts signals are processed on right inputs
        self.assertEqual(self.block._signals_processed["input1"],
                         input1_signals)
        self.assertEqual(self.block._signals_processed["input2"],
                         input2_signals)

    def test_process_signals_on_default(self):
        """ Tests process_signals when there is a default explicit input
        """
        self.block_type = BlockWithDefaultInputSpecified
        self.configure_block({})

        # process signals on default input
        default_input_signal1 = Signal({"name": "default_s1"})
        default_input_signal2 = Signal({"name": "default_s2"})
        self.process_signals([default_input_signal1, default_input_signal2])

        # process signals on named inputs
        input1_signal1 = Signal({"name": "i1_s1"})
        input1_signal2 = Signal({"name": "i1_s2"})
        self.process_signals([input1_signal1, input1_signal2], "input1")

        input2_signal1 = Signal({"name": "i2_s1"})
        input2_signal2 = Signal({"name": "i2_s2"})
        self.process_signals([input2_signal1, input2_signal2], "input2")

        # asserts no signals now make it to DEFAULT_TERMINAL since
        # there is an actual input defined
        self.assertNotIn(DEFAULT_TERMINAL, self.block._signals_processed)

        # assert signals were processes on expected inputs
        self.assertIn(default_input_signal1,
                      self.block._signals_processed["input1"])
        self.assertIn(default_input_signal2,
                      self.block._signals_processed["input1"])
        self.assertIn(input1_signal1,
                      self.block._signals_processed["input1"])
        self.assertIn(input1_signal2,
                      self.block._signals_processed["input1"])
        self.assertIn(input2_signal1,
                      self.block._signals_processed["input2"])
        self.assertIn(input2_signal2,
                      self.block._signals_processed["input2"])
