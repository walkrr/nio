from nio.testing.modules.web.server import TestingWebServer


class TestingWebEngine(object):

    @classmethod
    def get(cls, port, host, config=None):
        return TestingWebServer()

    @classmethod
    def remove_server(cls, server):
        pass

    @classmethod
    def get_servers(cls):
        return []

    @classmethod
    def configure(cls, configuration):
        """ Configure Web Server """
        pass

    @classmethod
    def get_name(cls):
        """ Returns server name """
        pass

    @classmethod
    def get_version(cls):
        """ Returns web server version """
        pass

    @classmethod
    def start(cls, callback=None):
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
