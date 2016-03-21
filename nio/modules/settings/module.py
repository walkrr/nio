from nio.modules.settings import Settings
from nio.modules.module import Module


class SettingsModule(Module):

    def proxy_settings_class(self, settings_class):
        Settings.proxy(settings_class)

    def finalize(self):
        Settings.unproxy()
        super().finalize()

    def get_module_order(self):
        return 1
