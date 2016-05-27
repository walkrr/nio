from nio.modules.web.handlers.web import WebHandler


class StaticHandler(WebHandler):

    def __init__(self, route):
        """ Create a new StaticHandler instance.

        Args:
            route: uri path

        """
        super().__init__(route)

    def handle(self, request, response):
        """ Handles given request

        Args:
            request: web request
            response: web response

        Returns:
            HTTP response
        """
        raise NotImplementedError()
