"""
  NIO test support base class

"""
import logging.config
import multiprocessing
from unittest import TestCase

from nio.modules.context import ModuleContext
from nio.modules.initializer import ModuleInitializer

# Testing module implementations
from nio.util.support.modules.scheduler.module import TestingSchedulerModule
from nio.util.support.modules.persistence.module \
    import TestingPersistenceModule
from nio.util.support.modules.communication.module \
    import TestingCommunicationModule
from nio.util.support.modules.security.module import TestingSecurityModule
from nio.util.support.modules.web.module import TestingWebModule


class NIOTestCase(TestCase):

    """ Base Unit Test case class

    Allows to customize environment information when
    running NIO unit tests

    """

    def __init__(self, methodName='runTests'):
        super().__init__(methodName)

        logging.config.dictConfig(self.get_logging_config())

    def get_persistence_module_context(self):
        return ModuleContext()

    def get_scheduler_module_context(self):
        return ModuleContext()

    def get_security_module_context(self):
        return ModuleContext()

    def get_communication_module_context(self):
        return ModuleContext()

    def get_web_module_context(self):
        return ModuleContext()

    def setupModules(self):
        self._module_initializer = ModuleInitializer()
        for module_name in self.get_test_modules():
            self._module_initializer.register_module(
                self.get_module(module_name),
                getattr(self, 'get_{}_module_context'.format(module_name))())

        # Perform a safe initialization in case a proxy never got cleaned up
        self._module_initializer.initialize(safe=True)

    def get_module(self, module_name):
        known_modules = {
            'scheduler': TestingSchedulerModule,
            'persistence': TestingPersistenceModule,
            'security': TestingSecurityModule,
            'communication': TestingCommunicationModule,
            'web': TestingWebModule
        }
        if module_name not in known_modules:
            raise ValueError("{} is not a valid module".format(module_name))
        return known_modules.get(module_name)()

    def tearDownModules(self):
        # Perform a safe finalization in case anything wasn't proxied
        # originally
        self._module_initializer.finalize(safe=True)

    def get_test_modules(self):
        """ Returns set of modules to load during test
        Override this method to customize which modules you want to load
        during a test
        """
        return {'scheduler', 'persistence'}

    def setUpSettings(self):
        """ Sets Settings before running a unit test """
        pass

    def get_logging_config(self):
        return {
            "version": 1,
            "formatters": {
                "default": {
                    "format": ("[%(niotime)s] NIO [%(levelname)s] "
                               "[%(context)s] %(message)s")
                }
            },
            "filters": {
                "niofilter": {
                    "()": "nio.util.logging.filter.NIOFilter"
                }
            },
            "handlers": {
                "default": {
                    "level": "NOTSET",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                    "filters": ["niofilter"]
                }
            },
            "root": {
                "handlers": ["default"]
            }
        }

    def setUp(self):
        super().setUp()
        try:
            multiprocessing.set_start_method('spawn')
        except Exception as e:
            # ignore this error
            if isinstance(e, RuntimeError) \
                    and "context has already been set" in str(e):
                pass
            else:
                print('Setting multiprocess start method, details: {0}'.
                      format(str(e)))
        # Initialize settings
        self.setUpSettings()
        # setup Modules
        self.setupModules()

    def tearDown(self):
        super().tearDown()
        self.tearDownModules()

    def get_provider_settings(self):
        """ Override this method for specifying settings
        for the config provider
        """
        return {}


class NIOTestCaseNoModules(NIOTestCase):

    """ NIO Test case that don't need to use modules

    """

    def get_test_modules(self):
        return set()

    def setupModules(self):
        pass  # Not using functionality modules

    def tearDownModules(self):
        pass  # Not using functionality modules
