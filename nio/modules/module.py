from sys import maxsize


class Module(object):

    """ A base class for defining a module interface or implementation """

    def initialize(self, context):
        """ Override this method to perform actions on initialization.

        Typically, during initialization, a module will want to proxy some
        class definitions and perform some additional setup items.

        Args:
            context (ModuleContext): Information pertaining to this module

        Returns:
            None - the return is ignored
        """
        pass

    def finalize(self):
        """ Override this method to perform actions on finalization.

        Typically, during finalization, a module will want to unproxy the
        classes it proxied when it initialized. There may also be some
        additional clean up items.

        Returns:
            None - the return is ignored
        """
        pass

    def get_module_order(self):
        """ Override this method to set the precedence for this module.

        This method should return an int specifying when this module should
        be initialized and finalized. Modules will be initialized in the
        order low-to-high and will be finalized in the reverse order. For
        example, a module with an order of 10 will be initialized before a
        module with an order of 20, but will be finalized after it.

        Defaults to a very large number, meaning it is initialized after the
        other modules.

        Returns:
            int: The order this module should be initialized
        """
        return maxsize
