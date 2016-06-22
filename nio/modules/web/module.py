from nio.modules.web import WebEngine, WebServer
from nio.modules.web.http import Request, Response
from nio.modules.module import Module


class WebModule(Module):

    def proxy_web_engine_class(self, web_engine_cls):
        WebEngine.proxy(web_engine_cls)

    def proxy_web_server_class(self, web_server_cls):
        WebServer.proxy(web_server_cls)

    def proxy_request_class(self, request_cls):
        Request.proxy(request_cls)

    def proxy_response_class(self, response_cls):
        Response.proxy(response_cls)

    def finalize(self):
        WebEngine.unproxy()
        WebServer.unproxy()
        Request.unproxy()
        Response.unproxy()
        super().finalize()

    def get_module_order(self):
        return 40
