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
        """ Retrieves a request header

        Returns:
            Request header

        """
        return self.get_headers().get(header, default)

    def get_headers(self):
        """ Retrieves request headers

        Returns:
            Request headers as a dictionary of the form
            {"[header_name]":"[header_value]"}

        """
        raise NotImplementedError()

    def get_method(self):
        """ Retrieves request method

        Returns:
            Request method

        """
        raise NotImplementedError()
