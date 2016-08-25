from nio.modules.context import ModuleContext
from nio.testing.modules.scheduler.scheduler_helper import \
    SchedulerHelperTesting
from nio.util.scheduler.job import Job
from nio.util.scheduler.scheduler import Scheduler
from nio.modules.scheduler.module import SchedulerModule


class TestingSchedulerModule(SchedulerModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_job_class(Job)

        # make scheduler use a SchedulerHelper designed for testing which
        # adds functionality to simulate 'jumps' in time
        Scheduler._scheduler_helper_class = SchedulerHelperTesting

        Scheduler.do_configure(context)
        Scheduler.do_start()

    def finalize(self):
        Scheduler.do_stop()
        super().finalize()

    def prepare_core_context(self):

        context = ModuleContext()
        # set a fine resolution during tests
        context.min_interval = 0.01
        context.resolution = 0.01

        return context
