from nio.testing.modules.scheduler.scheduler import JumpAheadScheduler


class JumpAheadJob(object):

    def __init__(self, target, delta, repeatable, *args, **kwargs):
        self._job = JumpAheadScheduler.schedule_task(
            target, delta, repeatable, *args, **kwargs)

    def cancel(self):
        JumpAheadScheduler.unschedule(self._job)

    def jump_ahead(self, seconds):
        """ Jump the scheudler forward a certain number of seconds.

        This is useful in tests to simulate time passing for event-driven
        logic and temporal assertions.
        """
        JumpAheadScheduler.jump_ahead(seconds)
