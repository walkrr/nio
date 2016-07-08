from nio.modules.module import ModuleNotInitialized
from nio.util.logging import get_nio_logger
from nio.util.runner import RunnerStatus
from nio.util.scheduler.scheduler_helper import SchedulerHelper
from nio.util.scheduler.scheduler_thread import SchedulerThread


class Scheduler(object):

    """Singleton class to maintain and interact with an underlying Scheduler"""

    _scheduler_thread = None
    _sched_min_delta = 0.1
    _sched_resolution = 0.1
    _status = None

    @classmethod
    def configure(cls, context):
        cls._status = RunnerStatus.configuring
        # Load in the minimum delta and resolution from the config
        cls._sched_min_delta = context.min_interval
        cls._sched_resolution = context.resolution
        cls._status = RunnerStatus.configured

    @classmethod
    def schedule_task(cls, target, delta, repeatable, *args, **kwargs):
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
        if cls._status != RunnerStatus.started:
            raise ModuleNotInitialized("Scheduler module is not started")

        return cls._scheduler_thread.scheduler.add(target, delta, repeatable,
                                                   *args, **kwargs)

    @classmethod
    def unschedule(cls, job):
        """Remove a job from the scheduler.

        If the given job is not currently scheduled, this method has no effect.

        Args:
            job (APScheduler Job): The job to remove.

        Returns:
            None

        """
        get_nio_logger("NIOScheduler").debug("Un-scheduling %s" % job)
        cls._scheduler_thread.scheduler.cancel(job)

    @classmethod
    def stop(cls):
        cls._status = RunnerStatus.stopping
        try:
            if cls._scheduler_thread:
                cls._scheduler_thread.stop()
        except:
            get_nio_logger("NIOScheduler").debug("Exception while stopping",
                                                 exc_info=True)
        finally:
            cls._scheduler_thread = None
            cls._status = RunnerStatus.stopped

    @classmethod
    def start(cls):
        cls._status = RunnerStatus.starting
        get_nio_logger("NIOScheduler").info("Starting custom scheduler")
        try:
            cls._scheduler_thread = SchedulerThread(SchedulerHelper(
                resolution=cls._sched_resolution,
                min_delta=cls._sched_min_delta))
            cls._scheduler_thread.start()
            cls._status = RunnerStatus.started
            get_nio_logger("NIOScheduler").info("Scheduler started")
        except Exception:  # pragma: no cover (exception from ap)
            get_nio_logger("NIOScheduler").exception(
                "Scheduler failed to start")
            cls._status = RunnerStatus.error
            raise
