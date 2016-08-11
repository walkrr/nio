"""
  NIO block support base class
"""
from threading import Event
from collections import defaultdict

from nio.block.context import BlockContext
from nio.signal.status import StatusSignal
from nio.testing.block.router import TestingBlockRouter
from nio.testing.test_case import NIOTestCase


class NIOBlockTestCase(NIOTestCase):

    def setUp(self):
        super().setUp()
        # instantiate and configure testing router
        self._router = TestingBlockRouter()
        self._router.configure(self)

        self._signals_notified_event = Event()
        self._block_type = None
        self._block = None

        # support internal test case control over signal notifications
        self._signals_notified = defaultdict(list)
        self._last_signals_notified = defaultdict(list)
        self._last_output_notified = None
        self._management_signals_notified = []
        self._block_status = ""

    @property
    def block_type(self):
        """ Provides block type

        Returns:
            Block type
        """
        return self._block_type

    @block_type.setter
    def block_type(self, block_type):
        """ Provides block instance in use during test

        Returns:
            Block instance
        """
        self._block_type = block_type
        # when block type is changed enforce a new block creation
        self._block = None

    def on_signals_notified(self, signals, output_id):
        """ Receives block signals notification

        This method is intended to be overriden by block developer if desired.

        Args:
            signals (list): signals being notified
            output_id: output identifier
        """
        pass

    def on_management_signal_notified(self, signal):
        """ Receives block management signal notification

        This method is intended to be overriden by block developer if desired.

        Args:
            signal (Signal): management signal being notified
        """
        pass

    @property
    def signals_notified_event(self):
        """ Allows access to event to wait on for signal notifications

        Block developer is responsible for resetting this event within test
        in case of a multiple wait scenario

        Returns:
            Python Event instance
        """
        return self._signals_notified_event

    @property
    def block(self):
        """ Provides block instance in use during test

        Returns:
            Block instance
        """
        if not self._block:
            self._block = self.block_type()
        return self._block

    def configure_block(self, block_properties):
        """ Configures block by assigning properties

        Args:
            block_properties (dict): properties to assign
        """
        # Blocks should always have a 'name', but we'll let it pass in tests
        block_properties["name"] = block_properties.get("name", "default")
        self.block.configure(BlockContext(
            self._router,
            block_properties,
            'TestSuite',
            ''))

    def start_block(self):
        """ Starts block
        """
        self.block.start()

    def stop_block(self):
        """ Stops block
        """
        self.block.stop()

    def notify_signals(self, signals, output_id=None):
        """ Invokes block's notify_signals method

        If output_id is not specified, the block's default output is used

        Args:
            output_id: The identifier of the output terminal the signals are
                being notified to.

        Raises:
            ValueError if output_id specified is invalid
        """
        if output_id is None:
            output_id = self._get_default_output_id()
        elif not self.block.is_output_valid(output_id):
            raise ValueError("output id specified is invalid")

        self.block.notify_signals(signals, output_id)

    def notify_management_signal(self, signal):
        """ Forwards management signal to block

        Args:
            signal: Signal to forward
        """
        self.block.notify_management_signal(signal)

    def process_signals(self, signals, input_id=None):
        """ Invokes block's process_signals method

        If input_id is not specified, the block's default input is used

        Args:
            input_id: The identifier of the input terminal the signals are
                being delivered to.

        Raises:
            ValueError if input_id specified is invalid
        """
        if input_id is None:
            input_id = self._get_default_input_id()
        elif not self.block.is_input_valid(input_id):
            raise ValueError("input id specified is invalid")

        self.block.process_signals(signals, input_id)

    def signals_notified(self, output_id=None):
        """ Allows access to signals notified within test

        If no signal has been notified on specified output, the last output
        notified on is used.

        If output_id is specified, it then must be valid

        Args:
            output_id (str): output identifier

        Returns:
            signals notified

        Raises:
            ValueError if output_id is invalid
        """
        # if output_id is specified, it must be valid.
        if output_id is not None and \
           output_id not in self._last_signals_notified:
            raise ValueError("Invalid output id specified")

        # if a valid output_id is not provided, use last output notified on.
        if output_id is None:
            output_id = self._last_output_notified

        return self._signals_notified[output_id]

    def last_signal_notified(self, output_id=None):
        """ Provides last signal notified

        If no signal has been notified on specified output, the last output
        notified on is used.

        If output_id is specified, it then must be valid

        Args:
            output_id (str): output identifier

        Returns:
            last signal notified

        Raises:
            ValueError if output_id is invalid
        """
        # if output_id is specified, it must be valid.
        if output_id is not None and \
           output_id not in self._last_signals_notified:
            raise ValueError("Invalid output id specified")

        # if a valid output_id is not provided, use last output notified on.
        if output_id is None:
            output_id = self._last_output_notified

        return self._last_signals_notified[output_id][-1]

    def assert_num_signals_notified(self, num, output_id=None):
        """ Assert that the number of signals notified is a certain number.

        Args:
            num (int): number to check against
            output_id: The output id of the block to consider.
        """
        if output_id is None:
            output_id = self._get_default_output_id()
        self.assertEqual(len(self._signals_notified[output_id]), num)

    def assert_num_mgmt_signals_notified(self, num):
        """ Assert the number of management signals notified is a number.

        Args:
            num (int): number to check against
        """
        self.assertEqual(len(self._management_signals_notified), num)

    def assert_block_status(self, status):
        """ Asserts that block has a certain status

        Blocks will have a status of '' if they have not had a status
        reported yet.

        Args:
            status (BlockStatus.xxx): The BlockStatus enum value to have
        """
        self.assertEqual(self._block_status, status)

    def _internal_signals_notified(self, block, signals, output_id):
        """ Receives internal block signals notification

        Calls overrideable public method 'signals_notified'.

        """

        self.assertEqual(block, self.block)

        self._signals_notified[output_id].extend(signals)
        self._last_signals_notified[output_id] = signals
        self._last_output_notified = output_id

        # allow block developer to override
        self.on_signals_notified(signals, output_id)
        # set signals notified event, block developer is responsible for
        # resetting it within test in case of a multiple wait scenario
        self._signals_notified_event.set()

    def _internal_management_signal_notified(self, block, signal):
        """ Receives internal management signal notification

        Calls overrideable public method 'on_management_signal_notified'.

        """

        self.assertEqual(block, self.block)

        if isinstance(signal, StatusSignal):
            self._block_status = signal.status

        self._management_signals_notified.extend([signal])

        # allow block developer to override
        self.on_management_signal_notified(signal)

    def _get_default_input_id(self):
        """ Provides block's default input

        Raises:
            ValueError if block has no default input
        """
        if not self.block._default_input:
            raise ValueError("Block: {} has no default input".
                             format(self.block_type))
        return self.block._default_input.id

    def _get_default_output_id(self):
        """ Provides block's default output

        Raises:
            ValueError if block has no default output
        """
        if not self.block._default_output:
            raise ValueError("Block: {} has no default output".
                             format(self.block_type))
        return self.block._default_output.id
