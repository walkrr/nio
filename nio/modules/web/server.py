from nio.modules.proxy import ModuleProxy


class WebServer(ModuleProxy):

    """ A Web Server class

    A web server is created by a web engine and can be started, stopped, and
    maintains a list of handlers (WebHandler) that it can receive requests
    on.

    This will likely be implemented in the web module implementation.

    """

    @property
    def host(self):
        """ Provides server host """
        return None

    @property
    def port(self):
        """ Provides server port """
        return None

    def add_handler(self, handler):
        """ Adds a web handler

        Args:
            handler (WebHandler): Web handler

        """
        raise NotImplementedError()

    def start(self, configuration):
        """ Starts web server

        Args:
            configuration: Server configuration

        """
        raise NotImplementedError()

    def stop(self):
        """ Stops web server

        """
        raise NotImplementedError()
