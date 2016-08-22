from nio import Block
from nio.block.terminals import DEFAULT_TERMINAL

# Maps which output to use based on input during a process_signals
INPUT_OUTPUT_MAPPINGS = {
    DEFAULT_TERMINAL: DEFAULT_TERMINAL,
    "input1": "output1",
    "input2": "output2"
}


class _TestBlock(Block):

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        """ Forwards signals to block's notify_signals method.

        Args:
            signals (list): A list of signals to be processed by the block
            input_id: The identifier of the input terminal the signals are
                being delivered to
        """
        self.notify_signals(signals, INPUT_OUTPUT_MAPPINGS[input_id])
