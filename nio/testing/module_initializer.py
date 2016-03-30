from nio.modules.initializer import ModuleInitializer


class TestingModuleInitializer(ModuleInitializer):

    """ Allows to customize a module initializer for testing purposes """

    def __init__(self, test):
        super().__init__()
        # safe a test instance copy to delegate calls to it as needed
        self._test = test

    def _initialize_module(self, module, context, safe):
        """ Overrides module initialization

        Carries on with regular module initialization and in addition
        detects when testing module is initialized so that it can delegate
        the call to set settings on the test

        """
        super()._initialize_module(module, context, safe)

        # if it is the 'settings' module, allow test to set settings
        # before other modules get initialized
        module_name = self._test.get_module_name(module)
        if module_name == 'settings':
            self._test.set_settings()

    def get_context(self, module):
        """ Overrides initializer's get_context so that call can be routed
        to actual test
        """
        module_name = self._test.get_module_name(module)

        # make sure to call get_context on the test since it is a method
        # every test can redefine
        return self._test.get_context(module_name, module)
