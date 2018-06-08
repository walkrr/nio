"""
  NIO block support base class

"""
from uuid import uuid4

from collections import defaultdict
from nio.testing.test_case import NIOTestCase
from nio.router.base import BlockRouter
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL


class BlockRouterForTesting(BlockRouter):

    """ A testing router to be used in block test cases.

    Supports block tests by keeping track of signal counts per block and
    block status as provided by management signals.
    """

    def __init__(self):
        super().__init__()
        self._test_case = None
        self._block_signal_counts = {}
        self._block_status = {}

    def configure(self, test_case):
        """ Configures router by saving the test case being supported

        Args:
            test_case (NIOTestCase): test case to call when notifying signals

        """
        self._test_case = test_case

    def notify_signals(self, block, signals, output_id=None):
        """ Receives block signals.

         Keeps track of the signal count per block and per output id
         Forwards notification to test_case's '_internal_signals_notified'

        Args:
            block (Block): notifier block
            signals (list): signals being notified
            output_id: output identifier

        """
        if output_id is None:
            output_id = DEFAULT_TERMINAL

        self._block_signal_counts[block] = \
            self._block_signal_counts.get(block) or defaultdict(int)
        self._block_signal_counts[block][output_id] += len(signals)

        self._test_case._internal_signals_notified(block, signals, output_id)

    def get_signals_from_block(self, block=None, output_id=DEFAULT_TERMINAL):
        """ Provides signal count per block or for all blocks

        Args:
            block (Block): block instance
            output_id: output identifier

        Returns:
            The number of signals a block has notified.
            If block is None, return the total number of signals notified

        """
        if block is None:
            return sum([sum(blk.values()) for blk
                        in self._block_signal_counts.values()])

        block_counts = self._block_signal_counts.get(block)
        if block_counts is None:
            return 0

        return block_counts.get(output_id) or 0


class NIOBlockTestCase(NIOTestCase):

    """ Base Unit Test case class for blocks

    Allows block tests to see the signals that get notified and access some
    other data about them by setting up a router.

    Simply create the block you want to use and call configure_block with the
    properties the block should have.

    Example:
    b = MyTestableBlock()
    self.configure_block(b, {"loglevel": "DEBUG"})

    Now, whenever b notifies signals, the signals_notified function will be
    called in the test case.
    """

    def __init__(self, methodName='runTests'):
        super().__init__(methodName)
        self._router = BlockRouterForTesting()
        self.notified_signals = defaultdict(list)
        # support internal test case control over signal notifications
        self._last_output_notified = None
        # keep track of mgmt signals notified per block
        self._block_mgmt_signal_counts = defaultdict(int)

    def setUp(self):
        super().setUp()
        self._router.configure(self)

    def configure_block(self, block, block_properties):
        """ Configures block by assigning properties and router to given block

        Args:
            block (Block): block instance
            block_properties (dict): properties to assign

        """
        # Blocks should always have an 'id', but we'll let it pass in tests
        block_properties["id"] = block_properties.get("id", uuid4().hex)
        block.configure(BlockContext(
            self._router,
            block_properties,
            'TestSuite',
            '',
            mgmt_signal_handler=self.management_signal_notified))

    @property
    def last_notified(self):
        # keep this property as an alias for backwards compatibility
        # convert to previous form, a list of signals

        return defaultdict(list, ((output_id, [notified_signal for sublist in
                                              self.notified_signals[output_id]
                                              for notified_signal in sublist])
                                  for output_id in self.notified_signals))

    def last_signal_notified(self, output_id=None):
        """ Provides last signal notified

        If no signal has been notified on specified output, the last output
        notified on is used.

        If output_id is specified, it must be valid

        Args:
            output_id (str): output identifier

        Returns:
            last signal notified

        Raises:
            ValueError if output_id is invalid
        """
        # if output_id is specified, it must be valid.
        if output_id is not None and \
           output_id not in self.notified_signals:
            raise ValueError("Invalid output id specified")

        # if a valid output_id is not provided, use last output notified on.
        if output_id is None:
            output_id = self._last_output_notified

        return self.notified_signals[output_id][-1][-1]

    def _internal_signals_notified(self, block, signals, output_id):
        """ Receives internal block signals notification

        Calls overrideable public method 'signals_notified' and updates
        internal members that support block unit testing.

        """
        self._last_output_notified = output_id

        self.signals_notified(block, signals, output_id)

    def signals_notified(self, block, signals, output_id):
        """ Receives block signals notification

        This method can be overriden by block developer

        Args:
            block (Block): notifying block
            signals (list): signals being notified
            output_id: output identifier

        """
        self.notified_signals[output_id].append(signals)

    def management_signal_notified(self, signal):
        """ Receives block management signal notification

        Args:
            signal (Signal): signal being notified
        """
        # update per block signal counting
        self._block_mgmt_signal_counts[signal.block_id] += 1

    def assert_num_signals_notified(self, num, block=None,
                                    output_id=DEFAULT_TERMINAL):
        """ Assert that the number of signals notified is a certain number.

        Args:
            num (int): number to check against
            block (Block): the block which should have notified. If not
                included, all blocks will be considered.
            output_id: The output id of the block to consider.
        """
        signals = self._router.get_signals_from_block(block, output_id)
        self.assertEqual(num, signals)

    def assert_num_mgmt_signals_notified(self, num, block=None):
        """ Assert the number of management signals notified is a number.

        Args:
            num (int): number to check against
            block (Block): the block which should have notified. If not
                included, all blocks will be considered.
        """
        if block:
            self.assertEqual(
                num, self._block_mgmt_signal_counts[block.id()])
        else:
            self.assertEqual(
                num, sum(self._block_mgmt_signal_counts.values()))

    def assert_signal_notified(self, signal, position=None,
                               output_id=DEFAULT_TERMINAL):
        """ Assert that the given signal has been notified from the block 
        
        Args:
            signal (signal object): signal to assert has been notified from 
                the block
            position (int): the position of the signal in the notified_signals 
                list
            output_id (string): output id of the block
        """
        total_notified_signals = [notified_signal.to_dict() for sublist in
                                  self.notified_signals[output_id]
                                  for notified_signal in sublist]
        if position is not None:
            self.assertEqual(signal.to_dict(),
                             total_notified_signals[position])
        else:
            self.assertIn(signal.to_dict(), total_notified_signals)

    def assert_signal_list_notified(self, signal_list, position=None,
                                    output_id=DEFAULT_TERMINAL):
        """ Assert that the given signal list has been notified from the 
        block. The given list must match the order in which the signals were
        notified.
        
        Args:
            signal_list (list): list of signal objects to assert
            output_id (string): output terminal of the block to assert against
            position (int): position of the signal list in 
                notified_signals[output_id]
        """
        input_list = [signal.to_dict() for signal in signal_list]
        notified_lists = [[signal.to_dict() for signal in notified_list]
                          for notified_list in self.notified_signals[output_id]]

        if position is not None:
            self.assertListEqual(input_list, notified_lists[position])
        else:
            self.assertIn(input_list, notified_lists)

    def assert_last_signal_notified(self, signal, output_id=DEFAULT_TERMINAL):
        """ Assert that the last signal notified on the given output_id is
        equal to 'signal'. This is designed to be a convenience function
        for last_signal_notified functionality, and provides dict comparison.
        
        Args:
            signal (signal object): the signal to assert against
            output_id (string): output terminal of the block to assert against
        """
        self.assertDictEqual(self.last_signal_notified(output_id).to_dict(),
                             signal.to_dict())

    def assert_last_signal_list_notified(self, signal_list,
                                         output_id=DEFAULT_TERMINAL):
        """ Assert the given list was notified from the block. Provides dict
        comparison.

        Args:
            signal_list (list): The list of signals to assert was notified
        """
        notified_list = [signal.to_dict() for signal in
                         self.notified_signals[output_id][-1]]
        signal_dict_list = [signal.to_dict() for signal in signal_list]

        self.assertListEqual(notified_list, signal_dict_list)

    def assert_block_status(self, block, status):
        """ Asserts that the given block has a certain block status

        Blocks will have a status of '' if they have not had a status
        reported yet.

        Args:
            block (Block): The block to check the status of
            status (BlockStatus.xxx): The BlockStatus enum value to have
        """
        self.assertEqual(self._router._block_status.get(block, ''), status)
