from nio.testing.modules.web.server import TestingWebServer


class TestingWebEngine(object):

    @staticmethod
    def get(port, host, config=None):
        return TestingWebServer()

    @staticmethod
    def remove_server(server):
        pass

    @staticmethod
    def get_servers():
        return []

    @staticmethod
    def configure(configuration):
        """ Configure Web Server """
        pass

    @staticmethod
    def get_name():
        """ Returns server name """
        pass

    @staticmethod
    def get_version():
        """ Returns web server version """
        pass

    @staticmethod
    def start(callback=None):
        """ Starts Web Server using configured params """
        pass

    @staticmethod
    def stop():
        """ Stops running Web Servers """
        pass

    @staticmethod
    def block():
        """ Blocks the Web Server until further request arrives """
        pass
