from nio.testing.modules.web.server import TestingWebServer


class TestingWebEngine(object):

    @classmethod
    def add_server(cls, port, host, config=None):
        return TestingWebServer()

    @classmethod
    def remove_server(cls, server):
        pass

    @classmethod
    def start(cls):
        """ Starts Web Server using configured params """
        pass

    @classmethod
    def stop(cls):
        """ Stops running Web Servers """
        pass

    @classmethod
    def block(cls):
        """ Blocks the Web Server until further request arrives """
        pass
