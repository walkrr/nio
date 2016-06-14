from nio.modules.proxy import ModuleProxy


class WebEngine(ModuleProxy):

    @staticmethod
    def get(port, host, configuration=None):
        """ Instantiates a web server

        Args:
            port (int): Port listening for requests
            host (str): Web server host address.
            configuration (dict): Contains additional server configuration,
                might contain additional ssl settings such as:
                ssl_certificate, ssl_private_key, ssl_certificate_chain

        Returns:
            The server if it already exists, or a new instantiated server
        """
        raise NotImplementedError()

    @staticmethod
    def remove_server(server):
        """ Stops and remove a server

        Args:
            server (WebServer): Server to remove
        """
        raise NotImplementedError()

    @staticmethod
    def start(callback=None):
        """ Starts Web engine

        Starts a web engine based on previously set configuration

        Args:
            callback: optional engine entry point

        """
        raise NotImplementedError()

    @staticmethod
    def stop():
        """ Stops engine and running Web Servers """
        raise NotImplementedError()

    @staticmethod
    def block():
        """ Blocks the Web engine

        This method is normally called from the main thread to block
        execution since likely each request will be handled by a separate
        thread.

        When stopping the engine, it is expected for it wait for all currently
        executing requests/threads to terminate.

        """
        raise NotImplementedError()
