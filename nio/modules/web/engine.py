from nio.modules.proxy import ModuleProxy


class WebEngine(ModuleProxy):

    @classmethod
    def add_server(cls, port, host=None, configuration=None):
        """ Creates and returns a web server

        Args:
            port (int): Port listening for requests
            host (str): Web server host address. Should default to the current
                host of the server.
            configuration (dict): Contains additional server configuration,
                might contain additional ssl settings such as:
                ssl_certificate, ssl_private_key, ssl_certificate_chain

        Returns:
            The server if it already exists, or a new instantiated server
        """
        raise NotImplementedError()

    @classmethod
    def remove_server(cls, server):
        """ Stops and remove a server

        Args:
            server (WebServer): Server to remove
        """
        raise NotImplementedError()

    @classmethod
    def start(cls):
        """ Starts Web engine

        Starts a web engine based on previously set configuration
        """
        raise NotImplementedError()

    @classmethod
    def stop(cls):
        """ Stops engine and running Web Servers """
        raise NotImplementedError()

    @classmethod
    def block(cls):
        """ Blocks the Web engine

        This method is normally called from the main thread to block
        execution since likely each request will be handled by a separate
        thread.

        When stopping the engine, it is expected for it wait for all currently
        executing requests/threads to terminate.

        """
        raise NotImplementedError()
