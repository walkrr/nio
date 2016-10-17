from nio.modules.web.handlers.web import WebHandler


class RESTHandler(WebHandler):

    def __init__(self, route):
        """ Create a new RESTHandler instance.

        Args:
            route: uri path

        """
        super().__init__(route)

    def is_collection(self):
        """ Specifies if the request result is a collection of items

        Returns:
            True if a collection is returned, False otherwise

        """
        return False

    def on_get(self, request, response):
        """ Get request handler

        The HTTP GET method is used to **read** (or retrieve) a
        representation of a resource

        Args:
            request: web request
            response: web response

        Returns:
            Web result

        """
        raise NotImplementedError()

    def on_post(self, request, response):
        """ Post request handler

        The POST verb is most-often utilized to **create** new resources

        Args:
            request: web request
            response: web response

        Returns:
            Web result

        """
        raise NotImplementedError()

    def on_put(self, request, response):
        """ Put request handler

        PUT is most-often utilized for **update** capabilities,
        PUT-ing to a known resource URI with the request body containing
        the newly-updated representation of the original resource.

        Args:
            request: web request
            response: web response

        Returns:
            Web result

        """
        raise NotImplementedError()

    def on_delete(self, request, response):
        """ Delete request handler

        Used to **delete** a resource identified by a URI.

        Args:
            request: web request
            response: web response

        Returns:
            Web result

        """
        raise NotImplementedError()

    def on_options(self, request, response):
        """ Options request handler, respond 200 by default

        We respond 200 by default for default CORS response. You are allowed
        to override with your own implementation.

        Args:
            request: web request
            response: web response

        Returns:
            Web result

        """

        response.set_status(200)
        response.set_body("")
