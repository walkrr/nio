from nio.modules.context import ModuleContext
from nio.testing.modules.settings import Settings
from nio.modules.settings.module import SettingsModule


class TestingSettingsModule(SettingsModule):

    def initialize(self, context):
        super().initialize(context)
        if not context.in_service:
            self.proxy_settings_class(Settings)
        else:
            # Don't proxy Settings, we want NotImplementedError to be raised
            # inside the service process
            pass

    def finalize(self):
        super().finalize()

    def prepare_core_context(self):
        context = ModuleContext()
        context.in_service = False
        return context

    def prepare_service_context(self, service_context=None):
        context = ModuleContext()
        context.in_service = True
        return context
