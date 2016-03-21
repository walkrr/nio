from nio.modules.settings import Settings
from nio.testing.test_case import NIOTestCase


class TestSetSettings(NIOTestCase):

    """ Tests that set_settings is called in the right spot (after initializing
    settings and before initializing any other module, and settings are
    available within tests . """

    def set_settings(self):

        Settings.set("test_section", "test_option", "test_value")

        # assert only Settings module has been initialized
        self.assertEqual(len(self._module_initializer._initialized_modules), 1)
        settings_module = self.get_module("settings")
        self.assertEqual(
            self._module_initializer._initialized_modules[0].__class__,
            settings_module.__class__)

    def test_set_settings(self):
        """ Makes sure settings are available within test """

        self.assertEqual(Settings.get("test_section", "test_option"),
                         "test_value")

        # assert that at this point all modules have been initialized
        self.assertEqual(len(self._module_initializer._initialized_modules),
                         len(self.get_test_modules()))
