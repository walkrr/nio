from nio.block.base import Block
from nio.block.terminals import output
from nio.signal.base import Signal
from nio.testing.block import NIOBlockTestCase


@output("output1")
@output("output2")
class BlockWithOutputs(Block):
    pass


@output("output1", default=True)
@output("output2")
class BlockWithDefaultOutputSpecified(Block):
    pass


class TestSignalsNotified(NIOBlockTestCase):

    def test_signals_default_terminal(self):
        """ Tests signals_notified when Block defines no output
        """
        self.block_type = Block
        self.configure_block({})

        # notify signals on default output
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        # don't specify any output
        self.notify_signals([default_output_signal1, default_output_signal2])
        # grab signals notified
        signals_notified = self.signals_notified()
        self.assertIn(default_output_signal1, signals_notified)
        self.assertIn(default_output_signal2, signals_notified)

        # notify signals on named outputs
        attempt_named_output = Signal({"name": "o1_s1"})
        with self.assertRaises(ValueError):
            self.notify_signals([attempt_named_output], "output1")

    def test_signals_notified(self):
        """ Tests signals_notified on a Block with outputs but no default
        """
        self.block_type = BlockWithOutputs
        self.configure_block({})

        # notify signals on named outputs
        attempt_default_signal = Signal({"name": "d1_s1"})
        with self.assertRaises(ValueError):
            self.notify_signals([attempt_default_signal])

        # notify signals on named outputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.notify_signals([output1_signal1, output1_signal2], "output1")

        # assert last signals notified
        self.assertIn(output1_signal1, self.signals_notified())
        self.assertIn(output1_signal2, self.signals_notified())

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        self.notify_signals([output2_signal1, output2_signal2], "output2")

        # assert output1 signals are not the signals notified by default anymore
        self.assertNotIn(output1_signal1, self.signals_notified())
        self.assertNotIn(output1_signal2, self.signals_notified())

        # assert last signals notified by default
        self.assertIn(output2_signal1, self.signals_notified())
        self.assertIn(output2_signal2, self.signals_notified())

        # assert last signal for specified outputs
        self.assertIn(output1_signal1, self.signals_notified("output1"))
        self.assertIn(output1_signal2, self.signals_notified("output1"))
        self.assertIn(output2_signal1, self.signals_notified("output2"))
        self.assertIn(output2_signal2, self.signals_notified("output2"))

        # assert that when output is specified, it must be valid when getting
        # last signal from it
        with self.assertRaises(ValueError):
            self.assertEqual(self.signals_notified("INVALID_OUTPUT"),
                             None)

    def test_signals_notified_with_default_specified(self):
        """ Assert signals_notified when there is a default explicit input
        """
        self.block_type = BlockWithDefaultOutputSpecified
        self.configure_block({})

        # notify signals on default input
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        self.notify_signals([default_output_signal1, default_output_signal2])

        # assert signals without naming and naming output yields
        # the same result
        self.assertIn(default_output_signal1, self.signals_notified())
        self.assertIn(default_output_signal2, self.signals_notified())
        self.assertIn(default_output_signal1, self.signals_notified("output1"))
        self.assertIn(default_output_signal2, self.signals_notified("output1"))

        # notify signals on named inputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.notify_signals([output1_signal1, output1_signal2], "output1")

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        self.notify_signals([output2_signal1, output2_signal2], "output2")

        # assert signals were processes on expected inputs
        self.assertIn(output1_signal1, self.signals_notified("output1"))
        self.assertIn(output1_signal2, self.signals_notified("output1"))

        self.assertIn(output2_signal1, self.signals_notified("output2"))
        self.assertIn(output2_signal2, self.signals_notified("output2"))
