class TestingRequest(object):

    def get_body(self):
        return None

    def get_identifier(self):
        return None

    def get_params(self):
        return {}

    def get_headers(self):
        return {}

    def get_method(self):
        return "UNKNOWN"


class TestingResponse(object):

    def set_header(self, header_name, header_value):
        pass

    def set_status(self, status, message=None):
        pass

    def set_body(self, body):
        pass
