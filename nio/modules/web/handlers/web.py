class WebHandler(object):

    """ Web Handler root class

    A web handler is characterized by a route and a handler method (handle)
    where the application would be handling the given request.

    """

    def __init__(self, route):
        """ Create a new WebHandler instance at a given route

        Args:
            route: uri path

        """
        self.route = route

    def handle(self, request, response):
        """ Handles given web request

        Args:
            request: web request
            response: web response

        Returns:
            HTTP response
        """
        raise NotImplementedError()
