from nio.testing.web_test_case import NIOWebTestCase


class TestWebModule(NIOWebTestCase):

    def test_web_module(self):
        """ Asserts web module bare functionality """
        # Most of our functionality is going to come from the web test case
        # This will make sure that we can adequately use that test case
        server = self.add_server(1111)
        self.remove_server(server)
