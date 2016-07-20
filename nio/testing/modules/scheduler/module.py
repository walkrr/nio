from nio.modules.context import ModuleContext
from nio.util.scheduler.job import Job
from nio.util.scheduler.scheduler import Scheduler
from nio.modules.scheduler.module import SchedulerModule


class TestingSchedulerModule(SchedulerModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_job_class(Job)

        Scheduler.instance().do_configure(context)
        Scheduler.instance().do_start()

    def finalize(self):
        Scheduler.instance().do_stop()
        super().finalize()

    def prepare_core_context(self):

        context = ModuleContext()
        context.min_interval = 0.1
        context.resolution = 0.1

        return context
