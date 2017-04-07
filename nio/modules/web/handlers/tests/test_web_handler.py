from unittest.mock import patch

from nio.modules.security import Authenticator
from nio.modules.web import WebHandler
from nio.testing.modules.web.http import TestingRequest, TestingResponse
from nio.testing.web_test_case import NIOWebTestCase


class PreflightRequest(TestingRequest):
    """ Simulates a pre-flight request
    """
    def get_method(self):
        return "OPTIONS"


class Request(TestingRequest):
    def __init__(self, method):
        self._method = method

    def get_method(self):
        return self._method


class MyWebHandler(WebHandler):
    def handle(self, request, response):
        return


class TestWebHandler(NIOWebTestCase):

    def test_non_preflight_request(self):
        """ Asserts that a GET request goes is authenticated by default        
        """
        web_handler = MyWebHandler("/")
        methods = ["GET", "POST", "PUT", "DELETE"]
        expected_athenticate_calls = 0

        with patch.object(Authenticator, "authenticate") \
                as patched_authenticate:
            for method in methods:
                request = Request(method)
                response = TestingResponse()

                web_handler.before_handler(request, response)
                web_handler.handle(request, request)
                web_handler.after_handler(request, response)

                expected_athenticate_calls += 1
                self.assertEqual(patched_authenticate.call_count,
                                 expected_athenticate_calls)

    def test_preflight_request(self):
        """ Asserts that an OPTIONS request bypasses authentication        
        """
        web_handler = MyWebHandler("/")

        request = PreflightRequest()
        response = TestingResponse()

        with patch.object(Authenticator, "authenticate") \
                as patched_authenticate:
            web_handler.before_handler(request, response)
            web_handler.handle(request, request)
            web_handler.after_handler(request, response)

            self.assertEqual(patched_authenticate.call_count, 0)
