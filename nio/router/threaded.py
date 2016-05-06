from nio.router.base import BlockRouter
from nio.util.threading import spawn


class ThreadedBlockRouter(BlockRouter):

    """A router that delivers signals asynchronously"""

    def deliver_signals(self, block_receiver, signals):
        """ Delivers signals to given block in a new thread """
        spawn(self.notify_signals_to_block, block_receiver, signals)
