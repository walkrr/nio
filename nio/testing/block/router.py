from nio.block.terminals import Terminal
from nio.block.terminals import TerminalType
from nio.router.base import BlockRouter


class TestingBlockRouter(BlockRouter):

    """ A testing router to be used in block test cases.

    Mostly forwards notifications to block test_case.
    """

    def __init__(self):
        super().__init__()
        self._test_case = None

    def configure(self, test_case):
        """ Configures router by saving the test case being supported

        Args:
            test_case (NIOTestCase): test case to call when notifying signals

        """
        self._test_case = test_case

    def notify_signals(self, block, signals, output_id):
        """ Receives block signals.

         Keeps track of the signal count per block and per output id
         Forwards notification to test_case's '_internal_signals_notified'

        Args:
            block (Block): notifier block
            signals (list): signals being notified
            output_id: output identifier

        """
        if output_id is None:
            output_id = \
                Terminal.get_default_terminal_on_class(block.__class__,
                                                       TerminalType.output)

        self._test_case._internal_signals_notified(block, signals, output_id)

    def notify_management_signal(self, block, signal):
        """ Receives management signal.

        Keeps track of the signal count per block
        Forwards signal to test_case's 'management_signal_notified' method

        Args:
            block (Block): notifier block
            signal (Signal): signal being notified

        """
        self._test_case._internal_management_signal_notified(block, signal)
