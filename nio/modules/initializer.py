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
from nio.modules.context import ModuleContext


class ModuleInitializer(object):

    """ A class that proxies and unproxies modules """

    def __init__(self):
        super().__init__()
        self.logger = get_nio_logger('ModuleInitializer')
        self._registered_modules = []
        self._initialized_modules = []

    def initialize(self, safe=False, raise_already_proxied=True):
        """ Initialize and proxy any registered module proxy implementations.

        This function will initialize any module implementations that have been
        registered with this ModuleInitializer.

        Args:
            safe (bool): True if you want the initialize to unproxy the proxy
                first, before trying to proxy it. Defaults to False
            raise_already_proxied (bool): True if you want to re-raise a
                ProxyAlreadyProxied exception, False will just log a warning
        """
        for module, context in sorted(
                self._registered_modules,
                key=lambda mod: mod[0].get_module_order()):

            # make sure module is not already initialized
            if module in self._initialized_modules:
                continue

            try:
                module.initialize(context)
            except ProxyAlreadyProxied:
                self.logger.warning(
                    "Interface implemented by module '{}' is already proxied".
                    format(module.__class__.__name__))
                if safe:
                    self.logger.warning("Unproxying and trying again")
                    module.finalize()
                    module.initialize(context)
                else:
                    if raise_already_proxied:
                        raise
                    continue

            self.logger.info("Module {} is initialized".
                             format(module.__class__.__name__))
            # Add this module to the list of modules that have been proxied
            self._initialized_modules.append(module)

    def register_module(self, module, context):
        """ Register a module and context to use for its initialization

        Args:
            module (Module): A nio module implementation
            context (ModuleContext): context to use when initializing module

        Raises:
            TypeError: if the implementation class is not a class
        """
        if not isinstance(module, Module):
            raise TypeError("Registered module must be an instance of Module")
        if not isinstance(context, ModuleContext):
            raise TypeError("Context must be an instance of ModuleContext")
        self._registered_modules.append((module, context))

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
