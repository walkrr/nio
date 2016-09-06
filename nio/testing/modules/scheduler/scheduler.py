from nio.util.scheduler.scheduler import SchedulerRunner


class JumpAheadSchedulerRunner(SchedulerRunner):
    """ Overrides SchedulerHelper allowing simulation of forward jumps in time
    """
    def __init__(self):
        super().__init__()
        # allows to simulate jumps in time during testing
        self.offset = 0

    def jump_ahead(self, seconds):
        """ Simulate a jump forward in time

        This will update the scheduler's offset a certain number of seconds
        in order to simulate time passing. Any scheduled jobs that should have
        fired during the time that passed will fire after scheduler thread
        takes control.

        Note: To facilitate the scheduler event processing thread to take
        control a 'sleep' call is invoked at the end of this method to
        avoid having to follow up with a 'sleep' call every time this method
        is invoked.

        Args:
            seconds (float): How many seconds to simulate passing in time.

        Raises:
            ValueError: If seconds is negative - can't go back in time
        """
        if float(seconds) < 0:
            raise ValueError("Cannot jump backwards in time")

        self.offset += seconds

        # have scheduler execute tasks that might be ready after this jump
        self._execute_pending_tasks()

    def _reset_scheduler(self):
        """ Reset our offset to 0 when the scheduler is reset """
        self.offset = 0
        super()._reset_scheduler()

    def _get_time(self):
        """ Overrides scheduler current time retrieval

        This time retrieval method is used when comparing against event_time
        """
        return super()._get_time() + self.offset

# Singleton reference to our jump ahead scheduler
JumpAheadScheduler = JumpAheadSchedulerRunner()
