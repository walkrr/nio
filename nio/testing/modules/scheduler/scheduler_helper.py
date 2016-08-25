from time import time

from nio.util.scheduler.scheduler_helper import SchedulerHelper


class SchedulerHelperTesting(SchedulerHelper):
    """ Overrides SchedulerHelper allowing simulation of forward jumps in time
    """

    def __init__(self, resolution, min_delta):
        """ Initializes scheduler.

        Args:
            resolution: Specifies the scheduler resolution, this value
                is used during sleeping operations when it is determined
                a wait is needed before determining the next event to be
                executed
            min_delta: minimum value to consider when scheduling a task
        """
        super().__init__(resolution, min_delta)
        # allows to simulate jumps in time during testing
        self._offset = 0

    def _get_time(self):
        """ Overrides scheduler current time retrieval

        This time retrieval method is used when comparing against event_time
        """
        return time() + self._offset

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset):
        """ Sets offset to use when retrieving current time

        Args:
            offset (float): offset in seconds
        """
        self._offset = offset
