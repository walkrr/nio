from nio.modules.context import ModuleContext
from nio.testing.modules.scheduler.job import JumpAheadJob
from nio.testing.modules.scheduler.scheduler import JumpAheadScheduler
from nio.modules.scheduler.module import SchedulerModule


class TestingSchedulerModule(SchedulerModule):

    def initialize(self, context):
        super().initialize(context)
        # For testing, use a job class that allows us to jump ahead in time
        self.proxy_job_class(JumpAheadJob)

        JumpAheadScheduler.do_configure(context)
        JumpAheadScheduler.do_start()

    def finalize(self):
        JumpAheadScheduler.do_stop()
        super().finalize()

    def prepare_core_context(self):
        context = ModuleContext()
        # set a fine resolution during tests
        context.min_interval = 0.01
        context.resolution = 0.01
        return context
