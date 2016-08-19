from nio.block.base import Block
from nio.block.terminals import DEFAULT_TERMINAL, output
from nio.signal.base import Signal
from nio.testing.block import NIOBlockTestCase


class TestBlockWithNoOutputs(NIOBlockTestCase):

    @property
    def block_type(self):
        return Block

    def test_last_signal_default_terminal(self):
        """ Tests last_signal_notified when no explicit output is defined
        """
        self.configure_block({})

        # notify signals on default output
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        self.notify_signals([default_output_signal1, default_output_signal2])
        self.assertEqual(self.last_signal_notified(), default_output_signal2)
        self.assertEqual(self.last_signal_notified(DEFAULT_TERMINAL),
                         default_output_signal2)

        # notify signals on named outputs fails since there is no named output
        attempt_named_output = Signal({"name": "o1_s1"})
        with self.assertRaises(ValueError):
            self.notify_signals([attempt_named_output], "output1")


@output("output1")
@output("output2")
class BlockWithOutputs(Block):
    pass


class TestBlockWithOutputs(NIOBlockTestCase):

    @property
    def block_type(self):
        return BlockWithOutputs

    def test_last_signal_with_outputs(self):
        """ Tests last_signal_notified when outputs are defined but no default
        """
        self.configure_block({})

        # notify signals on default output
        attempt_default_output_signal = Signal({"name": "default_s1"})
        # there is no default output
        with self.assertRaises(ValueError):
            self.notify_signals([attempt_default_output_signal])

        # notify signals on named outputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.notify_signals([output1_signal1, output1_signal2], "output1")

        # assert last signal
        self.assertEqual(self.last_signal_notified(), output1_signal2)

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        self.notify_signals([output2_signal1, output2_signal2], "output2")

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


@output("output1", default=True)
@output("output2")
class BlockWithDefaultOutputSpecified(Block):
    pass


class TestBlockWithDefaultOutputSpecified(NIOBlockTestCase):

    @property
    def block_type(self):
        return BlockWithDefaultOutputSpecified

    def test_last_signal_with_default_specified(self):
        """ Tests last_signal_notified when there is a default explicit output
        """
        self.configure_block({})

        # notify signals on default output
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        self.notify_signals([default_output_signal1, default_output_signal2])
        self.assertEqual(default_output_signal2, self.last_signal_notified())
        self.assertEqual(default_output_signal2,
                         self.last_signal_notified("output1"))

        # DEFAULT_TERMINAL is not valid when there is explicit default
        with self.assertRaises(ValueError):
            self.notify_signals([default_output_signal1], DEFAULT_TERMINAL)

        # notify signals on named outputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.notify_signals([output1_signal1, output1_signal2], "output1")

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        self.notify_signals([output2_signal1, output2_signal2], "output2")

        # assert signals were processed on expected outputs
        self.assertEqual(output1_signal2,
                         self.last_signal_notified("output1"))
        self.assertEqual(output2_signal2,
                         self.last_signal_notified("output2"))
