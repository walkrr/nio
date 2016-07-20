from nio.modules.module import ModuleNotInitialized
from nio.util.runner import RunnerStatus, Runner
from nio.util.scheduler.scheduler_helper import SchedulerHelper
from nio.util.scheduler.scheduler_thread import SchedulerThread


class Scheduler(object):

    """ Scheduler class implements a Singleton interface.

    The actual external methods are exposed by the _Impl class since this
    class's purpose is to provide a single instance access to the implementation
    """

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Scheduler.__instance is None:
            # Create and remember instance
            Scheduler.__instance = Scheduler.SchedulerImpl()

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    @classmethod
    def instance(cls):
        if not cls.__instance:
            return Scheduler()
        return cls.__instance

    class SchedulerImpl(Runner):

        def __init__(self):
            super().__init__()
            self._scheduler_thread = None
            self._sched_min_delta = 0.1
            self._sched_resolution = 0.1

        def configure(self, context):
            # Load in the minimum delta and resolution from the config
            self._sched_min_delta = context.min_interval
            self._sched_resolution = context.resolution

        def schedule_task(self, target, delta, repeatable, *args, **kwargs):
            """ Add the given task to the Scheduler.

            Args:
                target (callable): The task to be scheduled.
                delta (timedelta): The scheduling interval. The scheduler will
                    wait for this interval before running 'target' for the first
                    time.
                repeatable (bool): When False, 'target' is run only once.
                    Otherwise, it is run repeatedly at an interval defined by
                    'delta'.
                args: Positional arguments to be passed to 'target'.
                kwargs: Keyword arguments to be passed to 'target'.

            Returns:
                job (Job): The Job object.

            """
            if self.status != RunnerStatus.started:
                raise ModuleNotInitialized("Scheduler module is not started")

            return self._scheduler_thread.scheduler.add(
                target, delta, repeatable, *args, **kwargs)

        def unschedule(self, job):
            """Remove a job from the scheduler.

            If the given job is not currently scheduled, this method
            has no effect.

            Args:
                job (APScheduler Job): The job to remove.

            Returns:
                None

            """
            self.logger.debug("Un-scheduling %s" % job)
            self._scheduler_thread.scheduler.cancel(job)

        def stop(self):
            try:
                if self._scheduler_thread:
                    self._scheduler_thread.stop()
            finally:
                self._scheduler_thread = None

        def start(self):
            self._scheduler_thread = SchedulerThread(SchedulerHelper(
                resolution=self._sched_resolution,
                min_delta=self._sched_min_delta))
            self._scheduler_thread.start()
