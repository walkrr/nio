from nio.modules.proxy import ModuleProxy


class Request(ModuleProxy):

    """ A class encapsulating HTTP request information.

    Your module implementation will proxy this class with its own
    implementation details. An instance of a request will be passed to
    web handlers.

    """

    def get_body(self):
        """ Retrieves request body

        Returns:
            Request body

        """
        raise NotImplementedError()

    def get_identifier(self):
        """ Retrieves request identifier

        Returns:
            Request identifier

        """
        raise NotImplementedError()

    def get_params(self):
        """ Retrieves request params

        Returns:
            Request params

        """
        raise NotImplementedError()

    def get_header(self, header, default=None):
        """ Retrieves request headers

        Returns:
            Request headers

        """
        raise NotImplementedError()
