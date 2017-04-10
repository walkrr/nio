from nio import __version__ as nio_version
from nio.modules.security import Authenticator
from nio.modules.security.access import set_user


class WebHandler(object):

    """ Web Handler root class

    A web handler is characterized by a route and a handler method (handle)
    where the application would be handling the given request.

    """

    def __init__(self, route):
        """ Create a new WebHandler instance at a given route

        Args:
            route (str): uri path

        """
        self.route = route

    def before_handler(self, request, response):
        """ Provides an entry point before the request is handled

        Performs request authentication by default.

        A given handler wishing not to have authentication or its own 
        authentication implementation would be able to do so by 
        overriding this method.

        Args:
            request (Request): A request from the web module used to determine
                the user who is making this request
            response (Response): Web response

        Returns:
            User: A reference to the user making the request.

        Raises:
            Unauthorized: If it cannot determine the user making the request
        """
        if request.get_method() == 'OPTIONS':
            # pre-flight requests do not contain security info
            return

        set_user(Authenticator.authenticate(request))

    def handle(self, request, response):
        """ Handles given web request

        Args:
            request (Request): Web request
            response (Response): Web response

        Returns:
            HTTP response
        """
        raise NotImplementedError()

    def after_handler(self, request, response):
        """ Provides an entry point after the request is handled

        Args:
            request (Request): Web request
            response (Response): Web response
        """
        # Add nio server tag header
        response.set_header("Server", "n.io v{}".format(nio_version))
