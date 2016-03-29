""" An object that keeps track of modules and configurations.

A ModuleInitializer will have a list of module (nio.modules.module.Module)
objects as well as what configuration contexts they should be initialized
with. When instructed to initialize, the ModuleInitializer will determine
the proper order to initialize the modules based on the module class
definitions.
"""
from nio.util.logging import get_nio_logger
from nio.modules.proxy import ProxyNotProxied, ProxyAlreadyProxied
from nio.modules.module import Module


class ModuleInitializer(object):

    """ A class that proxies and unproxies modules """

    def __init__(self):
        super().__init__()
        self.logger = get_nio_logger('ModuleInitializer')
        self._registered_modules = []
        self._initialized_modules = []

    def initialize(self, safe=False):
        """ Initialize and proxy any registered module proxy implementations.

        This function will initialize any module implementations that have been
        registered with this ModuleInitializer.

        Args:
            safe (bool): True if you want the initialize to ignore modules
                trying to implement an already implemented interface.
                Defaults to False
        """
        for module in sorted(self._registered_modules,
                             key=lambda mod: mod.get_module_order()):

            # make sure module is not already initialized
            if module in self._initialized_modules:
                continue

            self._initialize_module(module, self.get_context(module), safe)

    def register_module(self, module):
        """ Register a module and context to use for its initialization

        Args:
            module (Module): A nio module implementation

        Raises:
            TypeError: if the implementation class is not a class
        """
        if not isinstance(module, Module):
            raise TypeError("Registered module must be an instance of Module")
        self._registered_modules.append(module)

    def finalize(self, safe=False):
        """ De-register and unproxy the registered modules on this initializer

        This will finalize the modules in the reverse order that they
        were proxied.

        Args:
            safe (bool): True if you want the finalize to succeed even if
                the modules are already unproxied. Defaults to False
        """
        for module in reversed(self._initialized_modules):
            if safe:
                try:
                    module.finalize()
                except ProxyNotProxied:
                    self.logger.warning(
                        "Ignoring ProxyNotProxied while finalizing {}".format(
                            module.__class__.__name__))
            else:
                module.finalize()
        self._initialized_modules[:] = []

    def _initialize_module(self, module, context, safe):
        try:
            module.initialize(context)
        except ProxyAlreadyProxied:
            self.logger.warning(
                "Interface implemented by module '{}' is already proxied".
                    format(module.__class__.__name__))
            if safe:
                # ignore a module trying to re-proxy when in safe mode
                return
            else:
                raise

        self.logger.info("Module {} is initialized".
                         format(module.__class__.__name__))

        # Add this module to the list of modules that have been proxied
        self._initialized_modules.append(module)

    def get_context(self, module):
        raise NotImplementedError()
