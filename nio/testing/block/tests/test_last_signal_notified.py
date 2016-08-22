from nio.testing.block.test_block import _TestBlock
from nio.block.terminals import DEFAULT_TERMINAL, input, output
from nio.signal.base import Signal
from nio.testing.block import NIOBlockTestCase


class TestBlockWithNoOutputs(NIOBlockTestCase):

    @property
    def block_type(self):
        return _TestBlock

    def test_last_signal_default_terminal(self):
        """ Tests last_signal_notified when no explicit output is defined
        """
        self.configure_block({})
        self.start_block()

        # process signals on default output
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        self.process_signals([default_output_signal1, default_output_signal2])
        self.assertEqual(self.last_signal_notified(), default_output_signal2)
        self.assertEqual(self.last_signal_notified(DEFAULT_TERMINAL),
                         default_output_signal2)

        self.stop_block()


@input("input1")
@input("input2")
@output("output1")
@output("output2")
class BlockWithOutputs(_TestBlock):
    pass


class TestBlockWithOutputs(NIOBlockTestCase):

    @property
    def block_type(self):
        return BlockWithOutputs

    def test_last_signal_with_outputs(self):
        """ Tests last_signal_notified when outputs are defined but no default
        """
        self.configure_block({})
        self.start_block()

        # process signals on default input
        attempt_default_input_signal = Signal({"name": "default_s1"})
        # there is no default output
        with self.assertRaises(ValueError):
            self.process_signals([attempt_default_input_signal])

        # process signals on named inputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.process_signals([output1_signal1, output1_signal2], "input1")

        # assert last signal
        self.assertEqual(self.last_signal_notified(), output1_signal2)

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        self.process_signals([output2_signal1, output2_signal2], "input2")

        # assert last signal
        self.assertEqual(self.last_signal_notified(), output2_signal2)

        # assert last signal for specified outputs
        self.assertEqual(self.last_signal_notified("output1"), output1_signal2)
        self.assertEqual(self.last_signal_notified("output2"), output2_signal2)

        # assert that when output is specified, it must be valid when getting
        # last signal from it
        with self.assertRaises(ValueError):
            self.assertEqual(self.last_signal_notified("INVALID_OUTPUT"),
                             None)

        self.stop_block()


@input("input1", default=True)
@input("input2")
@output("output1", default=True)
@output("output2")
class BlockWithDefaultOutputSpecified(_TestBlock):
    pass


class TestBlockWithDefaultOutputSpecified(NIOBlockTestCase):

    @property
    def block_type(self):
        return BlockWithDefaultOutputSpecified

    def test_last_signal_with_default_specified(self):
        """ Tests last_signal_notified when there is a default explicit output
        """
        self.configure_block({})
        self.start_block()

        # process signals on default input
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        self.process_signals([default_output_signal1, default_output_signal2])
        self.assertEqual(default_output_signal2, self.last_signal_notified())
        self.assertEqual(default_output_signal2,
                         self.last_signal_notified("output1"))

        # DEFAULT_TERMINAL is not valid when there is explicit default
        with self.assertRaises(ValueError):
            self.process_signals([default_output_signal1], DEFAULT_TERMINAL)

        # process signals on named inputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.process_signals([output1_signal1, output1_signal2], "input1")

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        self.process_signals([output2_signal1, output2_signal2], "input2")

        # assert signals were processed on expected outputs
        self.assertEqual(output1_signal2,
                         self.last_signal_notified("output1"))
        self.assertEqual(output2_signal2,
                         self.last_signal_notified("output2"))

        self.stop_block()
