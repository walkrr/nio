from nio.testing.modules.web.engine import TestingWebEngine
from nio.testing.modules.web.server import TestingWebServer
from nio.testing.modules.web.http import TestingRequest, TestingResponse
from nio.modules.web.module import WebModule


class TestingWebModule(WebModule):

    """ A version of the web module used for unit tests.

    This will proxy a simple WebEngine used for testing. Right now, this module
    implementation does nothing. A simple web server implementation is planned.
    """

    def initialize(self, context):
        super().initialize(context)
        self.proxy_web_engine_class(TestingWebEngine)
        self.proxy_web_server_class(TestingWebServer)
        self.proxy_request_class(TestingRequest)
        self.proxy_response_class(TestingResponse)

    def finalize(self):
        super().finalize()
